from rest_framework import viewsets, status
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.permissions import PermisoPorPerfil
from ..models import Pago
from ..serializers import PagoListSerializer, PagoUpdateSerializer


class PagoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]
    
    def get_queryset(self):
        queryset = Pago.objects.select_related('matricula','metodo_pago')

        query = self.request.query_params

        metodo_pago = query.get('metodo_pago')
        matricula = query.get('matricula')
        estado = query.get('estado')
        fecha_pago = query.get('fecha_pago')

        if metodo_pago:
            queryset=queryset.filter(metodo_pago__nombre__icontains=metodo_pago)

        if matricula:
            queryset=queryset.filter(
            Q(matricula__estudiante__nombre_completo__icontains=matricula) |
            Q(matricula__acudiente__nombre_completo__icontains=matricula) |
            Q(matricula__acudiente__numero_documento__icontains=matricula)
            )

        if estado is not None:
            estado = estado.lower() in ['true','1']
            queryset=queryset.filter(estado=estado)

        
        if fecha_pago:
            queryset=queryset.filter(fecha_pago__date=fecha_pago)

        return queryset
        

    def get_serializer_class(self):
        if self.action in ('create','update','partial_update'):
            return PagoUpdateSerializer
        return PagoListSerializer