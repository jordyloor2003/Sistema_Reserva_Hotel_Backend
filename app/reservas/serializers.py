from rest_framework import serializers
from .models import Reserva
from datetime import date

class ReservaSerializer(serializers.ModelSerializer):
    # Campo adicional solo para entrada
    tipo_pago = serializers.CharField(write_only=True, required=False, default='Efectivo')

    class Meta:
        model = Reserva
        fields = '__all__' 

    def get_resumen_pago(self, obj):
        if obj.pago:
            return {
                "monto": float(obj.pago.monto),
                "tipo_pago": obj.pago.tipo_pago,
                "estado": obj.pago.estado
            }
        return None

    def validate(self, data):
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        habitacion = data.get('habitacion')

        # Validación 1: fechas lógicas
        if fecha_fin and fecha_inicio and fecha_fin <= fecha_inicio:
            raise serializers.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")

        if fecha_inicio and fecha_inicio < date.today():
            raise serializers.ValidationError("No se puede reservar una fecha pasada.")

        # Validación 2: habitación disponible
        if habitacion and habitacion.estado.lower() != 'disponible':
            raise serializers.ValidationError(f"La habitación '{habitacion}' no está disponible actualmente.")

        # Validación 3: solapamiento de fechas para la misma habitación
        reservas_solapadas = Reserva.objects.filter(
            habitacion=habitacion,
            estado__in=['pendiente', 'activa'],
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
        )

        # Si estás editando una reserva existente, exclúyela
        if self.instance:
            reservas_solapadas = reservas_solapadas.exclude(id=self.instance.id)

        if reservas_solapadas.exists():
            raise serializers.ValidationError("La habitación ya está reservada en ese período.")

        return data

    def create(self, validated_data):
        # Extraemos tipo_pago para no pasarlo a Reserva.objects.create
        tipo_pago = validated_data.pop('tipo_pago', 'Efectivo')
        reserva = Reserva.objects.create(**validated_data)
        reserva.tipo_pago = tipo_pago  # solo si lo quieres almacenar temporalmente (opcional)
        return reserva