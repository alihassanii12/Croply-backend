from rest_framework.routers import DefaultRouter

from .views import FarmViewSet

router = DefaultRouter()
router.register('', FarmViewSet, basename='farm')

urlpatterns = router.urls
