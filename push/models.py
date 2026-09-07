from django.contrib.auth.models import User
from django.db import models


class PushSubscription(models.Model):
    """A browser Web Push subscription for a user."""

    user      = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='push_subscriptions'
    )
    endpoint  = models.TextField(unique=True)
    p256dh    = models.TextField()
    auth      = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} — {self.endpoint[:60]}'
