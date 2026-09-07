"""
Management command: send daily in-app weather notifications to all farmers.

Run manually:
    python manage.py send_weather_sms

Schedule with cron (every day at 7 AM):
    crontab -e
    0 7 * * * /home/kali/my_python_workspace/env/bin/python /home/kali/Desktop/Project/croply/backend/manage.py send_weather_sms
"""

import requests as http_requests

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import UserProfile
from notifications.models import Notification
from weather.views import OWM_URL, _advisory, _clean_location


def _fetch_weather(city: str) -> dict | None:
    api_key = settings.OPENWEATHER_API_KEY
    if not api_key or not city:
        return None
    try:
        resp = http_requests.get(
            OWM_URL,
            params={'q': city, 'appid': api_key, 'units': 'metric'},
            timeout=10,
        )
        resp.raise_for_status()
        raw     = resp.json()
        main    = raw.get('main', {})
        wind    = raw.get('wind', {})
        weather = raw.get('weather', [{}])[0]
        rain    = raw.get('rain', {})
        return {
            'location':    raw.get('name', city),
            'temp':        round(main.get('temp', 0), 1),
            'feels_like':  round(main.get('feels_like', 0), 1),
            'humidity':    main.get('humidity', 0),
            'description': weather.get('description', '').capitalize(),
            'wind_speed':  round(wind.get('speed', 0), 1),
            'rain_1h':     rain.get('1h', 0),
        }
    except Exception:
        return None


class Command(BaseCommand):
    help = 'Send daily in-app weather notifications to all farmers.'

    def handle(self, *args, **options):
        today   = timezone.localdate().strftime('%A, %d %B %Y')
        sent    = 0
        skipped = 0

        farmers = UserProfile.objects.filter(
            role=UserProfile.ROLE_FARMER,
        ).select_related('user')

        self.stdout.write(f'Processing {farmers.count()} farmers…')

        for profile in farmers:
            location = profile.location.strip()

            if not location:
                self.stdout.write(
                    self.style.WARNING(f'  [{profile.user.email}] No location — skipped.')
                )
                skipped += 1
                continue

            city = _clean_location(location)
            w    = _fetch_weather(city)

            if not w:
                self.stdout.write(
                    self.style.WARNING(
                        f'  [{profile.user.email}] Weather fetch failed for "{city}" — skipped.'
                    )
                )
                skipped += 1
                continue

            advisory = _advisory(w)

            message = (
                f"{w['description']} | {w['temp']}°C (feels {w['feels_like']}°C) | "
                f"Humidity {w['humidity']}% | Wind {w['wind_speed']} m/s"
                f"\n\nFarm Advisory: {advisory}"
            )

            Notification.objects.create(
                user=profile.user,
                title=f"Weather Update — {w['location']} ({today})",
                message=message,
            )

            self.stdout.write(
                self.style.SUCCESS(f'  [{profile.user.email}] Notification created.')
            )
            sent += 1

        self.stdout.write(
            self.style.SUCCESS(f'\nDone. Notified: {sent} | Skipped: {skipped}')
        )
