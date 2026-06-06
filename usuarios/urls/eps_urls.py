from rest_framework.routers import DefaultRouter
from ..views import EpsView

router = DefaultRouter()
router.register(r'eps', EpsView, basename='eps')

urlpatterns = router.urls