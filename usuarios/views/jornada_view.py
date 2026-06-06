from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from backend.permissions import PermisoPorPerfil
from ..serializers import JornadaSerializer
from ..models import Jornada

class JornadaViewSet(viewsets.ModelViewSet): 
    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    serializer_class = JornadaSerializer
    queryset = Jornada.objects.all()