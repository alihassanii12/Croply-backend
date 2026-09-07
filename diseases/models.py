from django.db import models


class Disease(models.Model):
    """A plant disease class known by the trained model."""

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text='Raw model class name, e.g. "Tomato___Late_blight".',
    )
    display_name = models.CharField(max_length=255, blank=True)
    plant = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    symptoms = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    prevention = models.TextField(blank=True)
    is_healthy = models.BooleanField(default=False)

    class Meta:
        ordering = ['plant', 'display_name']

    def __str__(self):
        return self.display_name or self.name
