from rest_framework.routers import DefaultRouter
from .views import PagoViewSet

router = DefaultRouter()
router.register(r'pagos', PagoViewSet, basename='pagos')

urlpatterns = router.urls
