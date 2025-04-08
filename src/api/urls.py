from django.urls import path
from . import views



urlpatterns = [
    path('', views.getRoutes, name="routes"),
    path('flow-data/', views.saveSensorData, name="flow-data-create"),
    path('flow-data/user/', views.getUserFlowData, name="flow-data-user"),
    path('token/recharge/', views.rechargeToken, name="token-recharge"),
    path('token/history/', views.getTokenHistory, name="token-history"),
]
