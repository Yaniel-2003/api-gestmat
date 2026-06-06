from rest_framework.routers import DefaultRouter
from ..views import MetodoPagoView

router = DefaultRouter()
router.register(r'metodo_pago', MetodoPagoView, basename='metodo_pago')

urlpatterns = router.urls