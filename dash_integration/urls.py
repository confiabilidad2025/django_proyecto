# dash_integration/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashapp/', views.dash_view, name='dash_view'),
]
