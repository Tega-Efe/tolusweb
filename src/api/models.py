from django.db import models
from django.conf import settings
from base.models import CustomUser

class FlowData(models.Model):
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='flow_data',
        null=True,  # Allow null temporarily
        default=1   # Set default to your admin user ID
    )
    sensor_id = models.CharField(max_length=50, default='default')
    distributionID = models.IntegerField()
    flowRate = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"Distribution {self.distributionID} - User: {self.user.username if self.user else 'None'}"