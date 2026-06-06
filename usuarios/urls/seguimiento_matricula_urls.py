

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import SeguimientoMatriculaViewSet


router = DefaultRouter()

router.register(r'seguimiento_matricula', SeguimientoMatriculaViewSet, basename='seguimiento_matricula')

urlpatterns = [
    # Incluir todas las URLs generadas por el router
    path('', include(router.urls)),
]

