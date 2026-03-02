from django.urls import path
from . import status_views

urlpatterns = [
    path('', status_views.status_view, name='status'),
]
