from django.contrib.auth.models import User
from django.db import models

from diseases.models import Disease


class Scan(models.Model):
    """An uploaded leaf image with its model prediction."""

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scans',
    )
    image = models.ImageField(upload_to='scans/%Y/%m/%d/')
    predicted_class = models.CharField(max_length=255, blank=True)
    plant = models.CharField(max_length=100, blank=True)
    disease_name = models.CharField(max_length=255, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    top_predictions = models.JSONField(default=list, blank=True)
    disease = models.ForeignKey(
        Disease,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scans',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Scan #{self.pk} - {self.predicted_class or "pending"}'
