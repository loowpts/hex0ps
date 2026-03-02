"""
URL маршруты для WS ticket endpoint.
"""
from django.urls import path
from . import ticket_views

urlpatterns = [
    path('ticket/', ticket_views.issue_ws_ticket, name='terminal-ws-ticket'),
]
