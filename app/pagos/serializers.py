from rest_framework import serializers
from .models import Pago
from app.reservas.models import Reserva

class PagoSerializer(serializers.ModelSerializer):
    reserva_id = serializers.SerializerMethodField()

    class Meta:
        model = Pago
        fields = ['id', 'monto', 'fecha', 'tipo_pago', 'estado', 'reserva_id']

    def get_reserva_id(self, obj):
        reserva = Reserva.objects.filter(pago=obj).first()
        return reserva.id if reserva else None
