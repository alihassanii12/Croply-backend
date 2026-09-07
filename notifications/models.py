from django.contrib.auth.models import User
from django.db import models


class Notification(models.Model):
    """A per-user notification."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
