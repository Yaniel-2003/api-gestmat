from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import DocumentoMatriculaViewSet

router = DefaultRouter()
router.register(r'documento_matricula', DocumentoMatriculaViewSet, basename='documento_matricula')

urlpatterns = [
    path('', include(router.urls)),
]