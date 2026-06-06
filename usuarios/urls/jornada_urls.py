from rest_framework.routers import DefaultRouter
from ..views import JornadaViewSet

router = DefaultRouter()
router.register(r'jornada', JornadaViewSet, basename='jornada')

urlpatterns = router.urls