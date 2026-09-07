from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import WeatherLiveView, WeatherRecordViewSet

router = DefaultRouter()
router.register('', WeatherRecordViewSet, basename='weather')

urlpatterns = [
    path('live/', WeatherLiveView.as_view(), name='weather-live'),
] + router.urls
