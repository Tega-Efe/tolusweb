from django.db import models
from django.conf import settings
from base.models import CustomUser

from django.utils import timezone

class FormattedDateTimeField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        # Handle datetime objects directly
        if isinstance(value, timezone.datetime):
            return value
        
        value = super().to_python(value)
        if value is not None:
            if isinstance(value, str):
                return value.strftime('%d-%m-%Y %H:%M')
            return value
        return value

    def get_prep_value(self, value):
        if isinstance(value, str):
            try:
                return timezone.datetime.strptime(value, '%d-%m-%Y %H:%M')
            except (ValueError, TypeError):
                # If the string format doesn't match, try parsing as Django datetime
                try:
                    return super().get_prep_value(value)
                except (ValueError, TypeError):
                    pass
        # For datetime objects, return directly
        if isinstance(value, timezone.datetime):
            return value
        return super().get_prep_value(value)
    
class FlowData(models.Model):
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='flow_data',
        null=True,
        default=1
    )
    sensor_id = models.CharField(max_length=50)  # This will be our primary identifier
    flowRate = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    created = FormattedDateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"Sensor {self.sensor_id} - User: {self.user.username if self.user else 'None'}"
class TokenHistory(models.Model):
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='token_history'
    )
    sensor_id = models.CharField(max_length=50)
    token_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Amount of tokens purchased"
    )
    volume_limit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Total volume of water allocated (in liters)"
    )
    volume_used = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Volume of water consumed (in liters)"
    )
    remaining_volume = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Remaining volume of water (in liters)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this token is currently active"
    )
    start_date = FormattedDateTimeField(auto_now_add=True)
    last_updated = FormattedDateTimeField(
        auto_now_add=True,
        help_text="Last time token was recharged"
    )
    end_date = FormattedDateTimeField(
        null=True, 
        blank=True,
        help_text="When the allocated volume was fully consumed"
    )

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = "Token History"

    def __str__(self):
        status = "Active" if self.is_active else "Completed"
        return f"{self.user.username} - Sensor {self.sensor_id} - {self.remaining_volume}L ({status})"

    def save(self, *args, **kwargs):
        # Set initial remaining_volume if not set
        if not self.pk and self.remaining_volume is None:
            self.remaining_volume = self.volume_limit
            self.last_updated = self.start_date
        super().save(*args, **kwargs)