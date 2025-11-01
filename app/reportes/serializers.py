from rest_framework import serializers
from .models import Reporte
from app.reservas.models import Reserva
from app.pagos.models import Pago
from app.usuarios.models import Usuario
from app.usuarios.serializers import UsuarioSerializer

class ReporteSerializer(serializers.ModelSerializer):
    # Solo lectura: se muestra el objeto Usuario completo
    usuario_detalle = UsuarioSerializer(source='usuario', read_only=True)
    
    # Solo escritura: se envía el ID del usuario
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    class Meta:
        model = Reporte
        fields = ['id', 'tipo', 'fecha_reporte', 'usuario', 'usuario_detalle']


class ReporteReservaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    habitacion_tipo = serializers.CharField(source='habitacion.tipo', read_only=True)

    class Meta:
        model = Reserva
        fields = ['cliente_nombre', 'habitacion_tipo', 'fecha_inicio', 'fecha_fin', 'estado']


class ReporteIngresoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='reserva.cliente.nombre', read_only=True)
    habitacion_tipo = serializers.CharField(source='reserva.habitacion.tipo', read_only=True)

    class Meta:
        model = Pago
        fields = ['id', 'fecha', 'monto', 'tipo_pago', 'cliente_nombre', 'habitacion_tipo']