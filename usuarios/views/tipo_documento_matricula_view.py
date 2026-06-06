from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from backend.permissions import PermisoPorPerfil
from ..models import Tipo_documento_matricula
from ..serializers import TipoDocumentoMatriculaSerializer

class TipoDocumentoMatriculaView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    serializer_class = TipoDocumentoMatriculaSerializer
    queryset = Tipo_documento_matricula.objects.all()