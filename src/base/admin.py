from django.contrib import admin
from . import models
from .models import Waterflow

admin.site.register(Waterflow)
admin.site.register(models.CustomUser)

# Register your models here.
