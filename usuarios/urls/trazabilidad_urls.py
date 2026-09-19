from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import AcudienteViewSet, TrazabilidadViewSet

router = DefaultRouter()
router.register(r'acudientes', AcudienteViewSet, basename='acudiente')
router.register(r'trazabilidad', TrazabilidadViewSet, basename='trazabilidad')

urlpatterns = [
    path('', include(router.urls)),
]