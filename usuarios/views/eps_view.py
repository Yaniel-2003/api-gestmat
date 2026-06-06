from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from backend.permissions import PermisoPorPerfil
from ..models import Eps
from ..serializers import EpsSerializer

class EpsView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    serializer_class = EpsSerializer
    queryset = Eps.objects.all()