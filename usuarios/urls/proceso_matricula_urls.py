from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import ProcesoMatriculaViewSet

router = DefaultRouter()
# El basename es opcional si el ViewSet ya tiene un queryset, pero dejarlo no hace daño
router.register(r'procesomatricula', ProcesoMatriculaViewSet, basename='procesomatricula')

urlpatterns = [
    # Es mejor incluir las URLs del router dentro de la lista
    path('', include(router.urls)),
]