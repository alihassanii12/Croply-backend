from django.contrib.auth.models import User
from django.db import models


class Listing(models.Model):
    """A produce listing posted by a farmer."""

    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listings',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    unit = models.CharField(max_length=50, blank=True, default='kg')
    contact = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
