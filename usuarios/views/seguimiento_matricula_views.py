from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from backend.permissions import PermisoPorPerfil
from ..utils import registrar_auditoria
from ..models import Seguimiento_matricula
from ..serializers import (
    SeguimientoMatriculaListSerializer,
    SeguimientoMatriculaUpdateSerializer,
    Proceso_matricula,
    ProcesoMatriculaSerializer,
)


class ProgresoEstudianteViewSet(viewsets.ModelViewSet):

    queryset = Proceso_matricula.objects.filter(activo=True).order_by('orden')
    serializer_class = ProcesoMatriculaSerializer

    def list(self, request, *args, **kwargs):

        matricula_id = request.query_params.get('matricula_id')

        serializer = self.get_serializer(
            self.get_queryset(),
            many=True,
            context={'matricula_id': matricula_id}  # Pasar matricula_id al serializer
        )
        return Response(serializer.data)



class SeguimientoMatriculaViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    queryset = Seguimiento_matricula.objects.select_related('matricula', 'paso', 'usuario_actualiza')
    # Limitar métodos HTTP: solo permitir GET, POST, PATCH, HEAD, OPTIONS
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_serializer_class(self):

        if self.action in ['create', 'update', 'partial_update']:
            return SeguimientoMatriculaUpdateSerializer
        return SeguimientoMatriculaListSerializer

    def get_queryset(self):

        queryset = self.queryset
        matricula_id = self.request.query_params.get('matricula_id')
        paso_id = self.request.query_params.get('paso_id')

        if matricula_id:
            queryset = queryset.filter(matricula_id=matricula_id)
        if paso_id:
            queryset = queryset.filter(paso_id=paso_id)

        return queryset

    def perform_create(self, serializer):
        
        estado = serializer.validated_data.get('estado')
        if estado == 'completado' and not serializer.validated_data.get('fecha_completado'):
            # Si es completado pero no hay fecha, asignamos ahora
            instance = serializer.save(usuario_actualiza=self.request.user, fecha_completado=timezone.now())
        else:
            # En otros casos, solo asignar usuario
            instance = serializer.save(usuario_actualiza=self.request.user)
        registrar_auditoria(self.request, "CREACIÓN SEGUIMIENTO", f"Se creó seguimiento para matrícula ID {instance.matricula_id} - Paso: {instance.paso}")

    def perform_update(self, serializer):
        
        estado = serializer.validated_data.get('estado')
        if estado == 'completado' and not serializer.validated_data.get('fecha_completado'):
            instance = serializer.save(usuario_actualiza=self.request.user, fecha_completado=timezone.now())
        else:
            instance = serializer.save(usuario_actualiza=self.request.user)
        registrar_auditoria(self.request, "ACTUALIZACIÓN SEGUIMIENTO", f"Se actualizó seguimiento ID {instance.id} - Estado: {instance.estado}")

