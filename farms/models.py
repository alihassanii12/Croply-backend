from django.contrib.auth.models import User
from django.db import models


class Farm(models.Model):
    """A farm managed by a farmer user."""

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='farms',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    size_hectares = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
