from rest_framework.routers import DefaultRouter
from ..views.pago_views import PagoViewSet

router = DefaultRouter()

router.register(r'pagos', PagoViewSet, basename='pagos')

urlpatterns = router.urls
