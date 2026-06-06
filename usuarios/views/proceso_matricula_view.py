from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from backend.permissions import PermisoPorPerfil
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

