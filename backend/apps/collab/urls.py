from django.urls import path
from . import views

urlpatterns = [
    path('invite/', views.create_invite_view, name='collab-invite'),
    path('<uuid:invite_token>/', views.collab_info_view, name='collab-info'),
    path('<uuid:invite_token>/join/', views.join_collab_view, name='collab-join'),
    path('<uuid:invite_token>/request-control/', views.request_control_view, name='collab-request-control'),
]
