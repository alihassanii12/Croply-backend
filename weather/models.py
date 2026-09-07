from django.db import models


class WeatherRecord(models.Model):
    """A weather observation for a location."""

    location = models.CharField(max_length=255)
    temperature = models.FloatField(help_text='Temperature in Celsius.')
    humidity = models.FloatField(
        null=True,
        blank=True,
        help_text='Relative humidity in percent.',
    )
    rainfall = models.FloatField(
        null=True,
        blank=True,
        help_text='Rainfall in millimeters.',
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f'{self.location} @ {self.recorded_at:%Y-%m-%d %H:%M}'
