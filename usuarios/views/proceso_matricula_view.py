from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from backend.permissions import PermisoPorPerfil
from ..utils import registrar_auditoria
from ..models import Proceso_matricula
from ..serializers import ProcesoMatriculaConEstadoSerializer



class ProcesoMatriculaViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    serializer_class = ProcesoMatriculaConEstadoSerializer
    queryset = Proceso_matricula.objects.all()

    def list(self, request, *args, **kwargs):

        # Paso 1: Obtener el ID de la matrícula del query string
        matricula_id = request.query_params.get('matricula_id')
        
        # Paso 2: Crear el serializer (many=True porque queremos lista)
        # El segundo parámetro context es un diccionario que puede usar el serializer
        serializer = self.get_serializer(
            self.get_queryset(),  # Pasar la lista de pasos a serializar
            many=True,  # Indicar que es una lista
            context={'matricula_id': matricula_id}  # Pasar matricula_id para que el serializer lo use
        )
        
        # Paso 3: Devolver la respuesta JSON
        return Response(serializer.data)

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar_auditoria(self.request, "CREACIÓN", f"Se creó el paso de proceso '{instance.nombre_paso}'")

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar_auditoria(self.request, "ACTUALIZACIÓN", f"Se actualizó el paso '{instance.nombre_paso}' (ID: {instance.pk})")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        nombre = instance.nombre_paso
        instance.delete()
        registrar_auditoria(request, "ELIMINACIÓN", f"Se eliminó el paso de proceso '{nombre}'")
        return Response({'mensaje': 'Paso de proceso eliminado correctamente'}, status=status.HTTP_200_OK)
