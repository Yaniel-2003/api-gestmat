from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..models import Tipo_documento
from ..serializers import TipoDocumentoSerializer
from backend.permissions import PermisoPorPerfil


class TipoDocumentoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    queryset           = Tipo_documento.objects.all()
    serializer_class   = TipoDocumentoSerializer       # List y Write usan el mismo serializer
                                                        # porque el modelo solo tiene 2 campos planos

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'mensaje': 'Tipo de documento eliminado correctamente'}, status=status.HTTP_200_OK)