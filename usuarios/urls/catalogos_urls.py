from rest_framework.routers import DefaultRouter
from ..views.catalogos_views import (
    EpsViewSet, JornadaViewSet, MetodoPagoViewSet,
    TipoDocumentoViewSet, TipoDocumentoMatriculaViewSet,
    fecha_ingreso_actual
)

router = DefaultRouter()
router.register(r'eps', EpsViewSet, basename='eps')
router.register(r'jornada', JornadaViewSet, basename='jornada')
router.register(r'metodo_pago', MetodoPagoViewSet, basename='metodo_pago')
router.register(r'tipos-documento', TipoDocumentoViewSet, basename='tipo-documento')
router.register(r'tipo_doc_matricula', TipoDocumentoMatriculaViewSet, basename='tipo_doc_matricula')

from django.urls import path

urlpatterns = [
    path('fecha_ingreso_actual/', fecha_ingreso_actual, name='fecha_ingreso_actual'),
] + router.urls
