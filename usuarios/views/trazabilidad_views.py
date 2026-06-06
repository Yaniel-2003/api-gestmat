# views.py
from rest_framework import viewsets, permissions
from ..models import Trazabilidad
from ..serializers import TrazabilidadSerializer
from backend.permissions import PermisoPorPerfil # Tu permiso personalizado

class TrazabilidadViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint para ver la auditoría del sistema.
    Solo permite GET (list y retrieve).
    """
    queryset = Trazabilidad.objects.select_related('usuario').order_by('-fecha_hora')
    serializer_class = TrazabilidadSerializer
    permission_classes = [permissions.IsAuthenticated, PermisoPorPerfil]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Opcional: Filtrar por usuario o acción desde la URL
        usuario_id = self.request.query_params.get('usuario')
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)
        return queryset