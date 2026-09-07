"""
Signals for the marketplace app.

When a new Listing is created:
  1. Create an in-app Notification for every buyer.
  2. Send a Web Push notification to every buyer who has an active subscription.
"""

import json
import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender='marketplace.Listing')
def notify_buyers_on_new_listing(sender, instance, created, **kwargs):
    if not created:
        return  # Only fire on new listings

    # Import here to avoid circular imports at module load
    from accounts.models import UserProfile
    from notifications.models import Notification
    from push.models import PushSubscription

    title   = f'New listing: {instance.title}'
    message = (
        f'{instance.title} — PKR {instance.price} / {instance.unit}. '
        f'Posted by {instance.seller.get_full_name() or instance.seller.email}.'
    )

    # ── In-app notifications ───────────────────────────────────────────────
    buyer_users = [
        p.user
        for p in UserProfile.objects.filter(role=UserProfile.ROLE_BUYER)
        .select_related('user')
    ]

    Notification.objects.bulk_create([
        Notification(user=user, title=title, message=message)
        for user in buyer_users
    ])

    # ── Web Push ───────────────────────────────────────────────────────────
    vapid_private = getattr(settings, 'VAPID_PRIVATE_KEY', '')
    vapid_public  = getattr(settings, 'VAPID_PUBLIC_KEY', '')
    vapid_email   = getattr(settings, 'VAPID_CLAIMS_EMAIL', '')

    if not all([vapid_private, vapid_public, vapid_email]):
        logger.info('VAPID keys not configured — Web Push skipped.')
        return

    buyer_ids = [u.id for u in buyer_users]
    subscriptions = PushSubscription.objects.filter(user_id__in=buyer_ids)

    if not subscriptions.exists():
        return

    try:
        from pywebpush import webpush, WebPushException  # type: ignore
    except ImportError:
        logger.warning('pywebpush not installed — Web Push skipped.')
        return

    payload = json.dumps({
        'title':   title,
        'body':    message,
        'icon':    '/icon-192.png',
        'url':     '/marketplace',
    })

    dead_endpoints = []

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    'endpoint': sub.endpoint,
                    'keys': {
                        'p256dh': sub.p256dh,
                        'auth':   sub.auth,
                    },
                },
                data=payload,
                vapid_private_key=vapid_private,
                vapid_claims={
                    'sub': vapid_email,
                },
            )
        except WebPushException as exc:
            logger.error('WebPush failed for sub %s: %s', sub.id, exc)
            # 410 Gone = subscription expired/revoked
            if '410' in str(exc) or '404' in str(exc):
                dead_endpoints.append(sub.id)
        except Exception as exc:
            logger.error('WebPush unexpected error: %s', exc)

    if dead_endpoints:
        PushSubscription.objects.filter(id__in=dead_endpoints).delete()
