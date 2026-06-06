from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Q
from ..models import Curso
from ..serializers import CursoUpdateSerializer, CursoListSerializer
from backend.permissions import PermisoPorPerfil # Asegúrate de que esta ruta sea correcta en tu proyecto

class CursoViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    
    # Se recomienda que el queryset base incluya las optimizaciones necesarias
    def get_queryset(self):
        queryset = Curso.objects.select_related('jornada').all()

        busqueda = self.request.query_params.get('buscar')

        if busqueda:
            queryset = queryset.filter(
                Q(nombre_curso__icontains=busqueda)|
                Q(grado__icontains=busqueda)
            )

        list_estado = self.request.query_params.get('activo')
        list_jornada = self.request.query_params.get('jornada')

        if list_estado is not None:
            es_activo = list_estado.lower() in ['true', '1']
            queryset = queryset.filter(activo=es_activo)

        if list_jornada:
            queryset = queryset.filter(jornada=list_jornada)

        return queryset


    def get_serializer_class(self):
        # Usamos el serializador detallado para lectura y el de escritura para modificaciones
        if self.action in ['create', 'update', 'partial_update']:
            return CursoUpdateSerializer
        return CursoListSerializer

    

    @action(detail=True, methods=['put'], url_path='actualizar-cupo')
    def actualizar_cupo(self, request, pk=None):
        curso = self.get_object()
        cupo_disponible = request.data.get('cupo_disponible')

        if cupo_disponible is None:
            return Response({'error': 'Debes enviar el cupo disponible'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cupo_disponible = int(cupo_disponible)
        except ValueError:
             return Response({'error': 'El cupo debe ser un número entero válido'}, status=status.HTTP_400_BAD_REQUEST)


        if cupo_disponible > curso.cupo_total:
            return Response(
                {'error': f'El cupo disponible no puede ser mayor al cupo total ({curso.cupo_total})'},
                status=status.HTTP_400_BAD_REQUEST
            )

        curso.cupo_disponible = cupo_disponible
        curso.save()
        
        return Response(CursoListSerializer(curso).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):

        curso = self.get_object()
        curso.activo = not curso.activo
        curso.save()

        return Response({
            'mensaje': f'Curso {"activado" if curso.activo else "desactivado"} correctamente',
            'activo':  curso.activo
        }, status=status.HTTP_200_OK)