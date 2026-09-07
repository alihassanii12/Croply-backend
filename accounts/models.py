from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """Unified profile for both farmers and buyers."""

    ROLE_FARMER = 'farmer'
    ROLE_BUYER = 'buyer'

    ROLE_CHOICES = [
        (ROLE_FARMER, 'Farmer'),
        (ROLE_BUYER, 'Buyer'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        blank=True,
        null=True,
    )
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    google_id = models.CharField(
        max_length=255, blank=True, null=True, unique=True
    )
    avatar_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} ({self.role})'

    @property
    def is_farmer(self):
        return self.role == self.ROLE_FARMER

    @property
    def is_buyer(self):
        return self.role == self.ROLE_BUYER
