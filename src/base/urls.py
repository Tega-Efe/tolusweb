from django.urls import path

from . import views

urlpatterns = [
  path('login/', views.CustomLoginView.as_view(), name='login'),
  path('register/', views.RegisterPage.as_view(), name='register'),
  path('logout/', views.logout_view, name='logout'),

  path('', views.Waterflow.as_view(), name='waterflow'),
  path('waterflow/', views.Waterflow.as_view(), name='waterflow'),
]
