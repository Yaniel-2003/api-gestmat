from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import AcudienteViewSet, fotos_acudiente, eliminar_foto_acudiente

router = DefaultRouter()
router.register(r'acudientes', AcudienteViewSet, basename='acudiente')

urlpatterns = [
    # El router genera automáticamente el CRUD (/acudientes/, /acudientes/<id>/, etc.)
    path('', include(router.urls)),
    
    # Mantenemos las rutas específicas de fotos
    path('acudientes/<int:id>/fotos/', fotos_acudiente, name='fotos_acudiente'),
    path('acudientes/<int:id>/fotos/<int:foto_id>/', eliminar_foto_acudiente, name='eliminar_foto_acudiente'),
]