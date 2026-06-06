from rest_framework.routers import DefaultRouter
from ..views import TipoDocumentoMatriculaView

router = DefaultRouter()
router.register(r'tipo_doc_matricula', TipoDocumentoMatriculaView, basename='tipo_doc_matricula')

urlpatterns = router.urls