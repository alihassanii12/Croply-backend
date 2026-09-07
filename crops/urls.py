from rest_framework.routers import DefaultRouter

from .views import CropViewSet

router = DefaultRouter()
router.register('', CropViewSet, basename='crop')

urlpatterns = router.urls
