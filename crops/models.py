from django.db import models

from farms.models import Farm


class Crop(models.Model):
    """A crop planted on a farm."""

    STATUS_CHOICES = [
        ('planted', 'Planted'),
        ('growing', 'Growing'),
        ('harvested', 'Harvested'),
        ('failed', 'Failed'),
    ]

    name = models.CharField(max_length=255)
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='crops',
    )
    planted_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planted',
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.farm.name})'
