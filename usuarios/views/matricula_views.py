from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from backend.permissions import PermisoPorPerfil
from ..utils import registrar_auditoria
from rest_framework.utils import timezone
from ..serializers import MatriculaListSerializer, MatriculaUpdateSerializer, EstudianteListSerializer, AcudienteListSerializer
from matriculas.models import Matricula
from academico.models import Foto_Acudiente, Foto_Estudiante, Estudiante, Acudiente
import os

class MatriculaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        #Traemos todos los datos 
        #Traemos las foreingkey que nececitamos 
        queryset = Matricula.objects.select_related('estudiante', 'acudiente', 'curso', 'jornada')#.prefetch_related('fotos')
        
        #Filtro seguridad 
        if self.request.user.perfil.nombre_perfil != 'Administrador':
            queryset = queryset.filter(acudiente__usuario=self.request.user)

        #Filtros dinamicos 
        busqueda = self.request.query_params.get('buscar')

        if busqueda :
            queryset = queryset.filter(
                Q(estudiante__nombre_completo__icontains=busqueda) |
                Q(acudiente__nombre_completo__icontains=busqueda)
            )


        nombre_estu = self.request.query_params.get('nombre_completo')
        nombre_acu = self.request.query_params.get('nombre_completo')
        curso_nam = self.request.query_params.get('nombre_curso')
        estado_mat = self.request.query_params.get('estado')

        if nombre_estu:
            #ingresamos a la tabla de estudiante
            queryset = queryset.filter(estudiante__nombre_completo__icontains=nombre_estu)
        if nombre_acu: 
            queryset = queryset.filter(acudiente__nombre_completo__icontains=nombre_acu)
        if curso_nam:
            queryset = queryset.filter(curso__nombre_curso__icontains=curso_nam)
        if estado_mat is not None:
            queryset = queryset.filter(estado=estado_mat.lower() in ['true', '1'])


        return queryset

    #CRUD       
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MatriculaUpdateSerializer
        return MatriculaListSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar_auditoria(self.request, "CREACIÓN", f"Se creó matrícula para {instance.estudiante} - Año {instance.year_lectivo} (ID: {instance.pk})")

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar_auditoria(self.request, "ACTUALIZACIÓN", f"Se actualizó la matrícula ID {instance.pk} - {instance.estudiante}")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        info = f"{instance.estudiante} - Año {instance.year_lectivo}"
        instance.delete()
        registrar_auditoria(request, "ELIMINACIÓN", f"Se eliminó la matrícula: {info}")
        return Response({'mensaje': 'Matrícula eliminada correctamente'}, status=status.HTTP_200_OK)
