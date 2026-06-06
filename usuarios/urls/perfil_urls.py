from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Importamos el ViewSet Y las funciones nuevas
from ..views.perfil_views import PerfilViewSet

router = DefaultRouter()
router.register(r'perfil', PerfilViewSet, basename='perfil')

urlpatterns = [
    # 1. Las rutas automáticas del ViewSet (CRUD)
    path('', include(router.urls)),
]