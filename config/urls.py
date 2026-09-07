"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/farms/', include('farms.urls')),
    path('api/crops/', include('crops.urls')),
    path('api/diseases/', include('diseases.urls')),
    path('api/scans/', include('scans.urls')),
    path('api/weather/', include('weather.urls')),
    path('api/marketplace/', include('marketplace.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/push/', include('push.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
