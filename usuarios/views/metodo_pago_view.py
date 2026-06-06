from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.permissions import PermisoPorPerfil
from ..models import Metodo_pago
from ..serializers import MetodoPagoSerializer

class MetodoPagoView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    serializer_class = MetodoPagoSerializer
    queryset = Metodo_pago.objects.all()