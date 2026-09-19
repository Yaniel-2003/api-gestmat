# views.py
from rest_framework import viewsets, permissions
from django.db.models import Q
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
        
        usuario_id = self.request.query_params.get('usuario')
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)
            
        busqueda = self.request.query_params.get('buscar')
        if busqueda:
            queryset = queryset.filter(
                Q(usuario__username__icontains=busqueda) |
                Q(usuario__first_name__icontains=busqueda) |
                Q(usuario__last_name__icontains=busqueda) |
                Q(accion__icontains=busqueda) |
                Q(descripcion__icontains=busqueda)
            )
            
        accion = self.request.query_params.get('accion')
        if accion:
            queryset = queryset.filter(accion__icontains=accion)
            
        return queryset