from django.urls import path
from . import changelog_views

urlpatterns = [
    path('', changelog_views.changelog_view, name='changelog'),
]
