from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import UsuarioViewSet, fotos_usuario, eliminar_foto_usuario

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')

urlpatterns = [
    path('', include(router.urls)),
    path('usuarios/<int:id>/fotos/',                fotos_usuario),
    path('usuarios/<int:id>/fotos/<int:foto_id>/',  eliminar_foto_usuario),
]