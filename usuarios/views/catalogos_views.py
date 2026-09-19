from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.permissions import PermisoPorPerfil
from academico.models import Eps, Jornada
from pagos.models import Metodo_pago
from ..models import Tipo_documento
from matriculas.models import Tipo_documento_matricula
from ..serializers import (
    EpsSerializer, JornadaSerializer, MetodoPagoSerializer,
    TipoDocumentoSerializer, TipoDocumentoMatriculaSerializer
)
from ..utils import registrar_auditoria
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from matriculas.models import ConfiguracionMesIngreso

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fecha_ingreso_actual(request):
    current_month = timezone.now().month
    current_year = timezone.now().year
    config = ConfiguracionMesIngreso.objects.filter(
        mes=current_month, 
        year_lectivo=current_year, 
        activo=True
    ).first()
    
    fecha = config.fecha_inicio if config else timezone.now().date()
    return Response({'fecha_inicio': fecha.strftime('%Y-%m-%d')})


# ================================================================================
# VIEWSETS DE TABLAS CATÁLOGO
# ================================================================================
# Estas tablas contienen datos de referencia que son consumidos por las tablas
# principales (Estudiante, Matrícula, Pago, etc.) a través de ForeignKeys.
# Se consolidan en un solo archivo para mantener el código organizado.
# ================================================================================


class EpsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    serializer_class = EpsSerializer
    queryset = Eps.objects.all()
    pagination_class = None

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar_auditoria(self.request, "CREACIÓN", f"Se creó la EPS '{instance.nombre_eps}'")

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar_auditoria(self.request, "ACTUALIZACIÓN", f"Se actualizó la EPS '{instance.nombre_eps}' (ID: {instance.pk})")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        nombre = instance.nombre_eps
        instance.delete()
        registrar_auditoria(request, "ELIMINACIÓN", f"Se eliminó la EPS '{nombre}'")
        return Response({'mensaje': 'EPS eliminada correctamente'}, status=status.HTTP_200_OK)


class JornadaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    serializer_class = JornadaSerializer
    queryset = Jornada.objects.all()
    pagination_class = None

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar_auditoria(self.request, "CREACIÓN", f"Se creó la jornada '{instance.nombre_jornada}'")

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar_auditoria(self.request, "ACTUALIZACIÓN", f"Se actualizó la jornada '{instance.nombre_jornada}' (ID: {instance.pk})")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        nombre = instance.nombre_jornada
        instance.delete()
        registrar_auditoria(request, "ELIMINACIÓN", f"Se eliminó la jornada '{nombre}'")
        return Response({'mensaje': 'Jornada eliminada correctamente'}, status=status.HTTP_200_OK)


class MetodoPagoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    serializer_class = MetodoPagoSerializer
    queryset = Metodo_pago.objects.all()
    pagination_class = None

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar_auditoria(self.request, "CREACIÓN", f"Se creó el método de pago '{instance.nombre}'")

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar_auditoria(self.request, "ACTUALIZACIÓN", f"Se actualizó el método de pago '{instance.nombre}' (ID: {instance.pk})")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        nombre = instance.nombre
        instance.delete()
        registrar_auditoria(request, "ELIMINACIÓN", f"Se eliminó el método de pago '{nombre}'")
        return Response({'mensaje': 'Método de pago eliminado correctamente'}, status=status.HTTP_200_OK)


class TipoDocumentoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    serializer_class = TipoDocumentoSerializer
    queryset = Tipo_documento.objects.all()
    pagination_class = None

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar_auditoria(self.request, "CREACIÓN", f"Se creó el tipo de documento '{instance.descripcion}' ({instance.sigla})")

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar_auditoria(self.request, "ACTUALIZACIÓN", f"Se actualizó el tipo de documento '{instance.descripcion}' (ID: {instance.pk})")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        descripcion = instance.descripcion
        instance.delete()
        registrar_auditoria(request, "ELIMINACIÓN", f"Se eliminó el tipo de documento '{descripcion}'")
        return Response({'mensaje': 'Tipo de documento eliminado correctamente'}, status=status.HTTP_200_OK)


class TipoDocumentoMatriculaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    serializer_class = TipoDocumentoMatriculaSerializer
    queryset = Tipo_documento_matricula.objects.all()
    pagination_class = None

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar_auditoria(self.request, "CREACIÓN", f"Se creó el tipo de documento de matrícula '{instance.descripcion}'")

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar_auditoria(self.request, "ACTUALIZACIÓN", f"Se actualizó el tipo de documento de matrícula '{instance.descripcion}' (ID: {instance.pk})")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        descripcion = instance.descripcion
        instance.delete()
        registrar_auditoria(request, "ELIMINACIÓN", f"Se eliminó el tipo de documento de matrícula '{descripcion}'")
        return Response({'mensaje': 'Tipo de documento de matrícula eliminado correctamente'}, status=status.HTTP_200_OK)
