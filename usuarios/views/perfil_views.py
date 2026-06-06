from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from ..models import Perfil
from ..serializers import PerfilListSerializer, PerfilUpdateSerializer
from backend.permissions import PermisoPorPerfil # Asegúrate de que esta ruta es correcta


class PerfilViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    lookup_field = 'id'

    def get_queryset(self):
        queryset = Perfil.objects.select_related('pagina_inicio').prefetch_related('paginas','Componentes').all()

        #Capturamos los parametros que se van a buscar
        perfilId = self.request.query_params.get('id')
        nombre = self.request.query_params.get('nombre_perfil')
        estado = self.request.query_params.get('activo')

        #Aplicamos los filtros dinamicos
        if nombre:
            queryset = queryset.filter(nombre_perfil__icontains=nombre)

        if perfilId:
            queryset = queryset.filter(id=perfilId)

        if estado is not None:
            #convertimos true en 1 y cualquier numero el false
           esActivo = estado.lower() in ['true','1']
           queryset = queryset.filter(activo=esActivo) 

        return queryset
    
    def get_serializer_class(self):
        #loigca de selecion de serializer (CRUD)
        if self.action in ['create','update','partial_update']:
            return PerfilUpdateSerializer
        return PerfilListSerializer