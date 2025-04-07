from django.db import models

# Create your models here.
class Note(models.Model):
    body = models.TextField(null=True, blank=True)
    device_id = models.CharField(max_length=255,null=True, blank=True)  # Add this line
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[:50]

