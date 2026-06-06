from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from backend.permissions import PermisoPorPerfil
from ..models import Pagina
from ..serializers import PaginaSerializer


class PaginaView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    serializer_class = PaginaSerializer
    queryset = Pagina.objects.all()
    
    