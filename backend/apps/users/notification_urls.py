from django.urls import path
from . import notification_views

urlpatterns = [
    path('', notification_views.notification_list_view, name='notification-list'),
    path('<int:notification_id>/read/', notification_views.notification_read_view, name='notification-read'),
    path('read-all/', notification_views.notification_read_all_view, name='notification-read-all'),
]
