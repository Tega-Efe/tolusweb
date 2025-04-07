from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes, name="routes"),
    path('flow-data/', views.saveSensorData, name="flow-data"),
    path('sensor-data/', views.saveSensorData, name='save-sensor-data'),
    path('update-flow-data/', views.updateUserFlowData, name='update-flow-data'),
    path('user-flow-data/', views.getUserFlowData, name='user-flow-data'),
]