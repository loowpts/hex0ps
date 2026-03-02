from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.auth_urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/tasks/', include('apps.tasks.urls')),
    path('api/ai/', include('apps.ai.urls')),
    path('api/interview/', include('apps.interview.urls')),
    path('api/notes/', include('apps.notes.urls')),
    path('api/certs/', include('apps.certs.urls')),
    path('api/collab/', include('apps.collab.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/roadmap/', include('apps.tasks.roadmap_urls')),
    path('api/daily/', include('apps.tasks.daily_urls')),
    path('api/terminal/', include('apps.terminal.ticket_urls')),
    path('api/playground/', include('apps.terminal.playground_urls')),
    path('api/recordings/', include('apps.terminal.recording_urls')),
    path('api/courses/', include('apps.courses.urls')),
    path('api/cheatsheets/', include('apps.cheatsheets.urls')),
    path('api/status/', include('apps.analytics.status_urls')),
    path('api/changelog/', include('apps.analytics.changelog_urls')),
    path('api/notifications/', include('apps.users.notification_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
