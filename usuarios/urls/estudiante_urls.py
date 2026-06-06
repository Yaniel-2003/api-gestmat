from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import EstudianteViewSet, fotos_estudiante, eliminar_fotos_estudiante

router = DefaultRouter()
router.register(r'estudiante', EstudianteViewSet, basename='estudiante')

urlpatterns = [
    path('', include(router.urls)),
    
    # Rutas para las fotos del estudiante
    path('estudiante/<int:id>/fotos/', fotos_estudiante, name='fotos_estudiante'),
    path('estudiante/<int:id>/fotos/<int:foto_id>/', eliminar_fotos_estudiante, name='eliminar_fotos_estudiante'),
]