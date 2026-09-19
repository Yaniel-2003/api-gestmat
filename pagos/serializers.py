from rest_framework import serializers
from .models import Pago, Metodo_pago, TarifaMatricula


class BaseSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='pk')
    class Meta:
        pass


class MetodoPagoSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model  = Metodo_pago
        fields = ['id', 'id_metodo_pago', 'nombre', 'descripcion', 'fecha_creacion']


class PagoListSerializer(BaseSerializer):
    # Importación diferida para evitar ciclos
    metodo_pago = MetodoPagoSerializer()

    class Meta(BaseSerializer.Meta):
        model  = Pago
        fields = ['id', 'matricula', 'fecha_pago', 'valor_pago', 'metodo_pago', 'estado_pago']


class PagoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Pago
        fields = ['matricula', 'fecha_pago', 'valor_pago', 'metodo_pago', 'estado_pago']

    def validate_valor_pago(self, value):
        if value <= 0:
            raise serializers.ValidationError('El valor del pago debe ser mayor a 0')
        return value


class TarifaMatriculaSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model  = TarifaMatricula
        fields = ['id', 'curso', 'year_lectivo', 'valor', 'descripcion', 'activo', 'fecha_creacion']
