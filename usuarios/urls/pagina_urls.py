from rest_framework.routers import DefaultRouter
from ..views import PaginaView

router = DefaultRouter()
router.register(r'pagina', PaginaView, basename='pagina')

urlpatterns = router.urls