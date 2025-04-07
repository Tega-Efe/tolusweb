from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes, name="routes"),
    path('flow-data/', views.saveFlowData, name="flow-data"),
    path('user-flow-data/', views.getUserFlowData, name='user-flow-data'),
]