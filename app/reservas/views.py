from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_yasg import openapi

from .models import Reserva
from .serializers import ReservaSerializer
from .filters import ReservaFilter
from app.pagos.models import Pago

@extend_schema(tags=['Reservas'])
class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all().order_by('-fecha_inicio')
    serializer_class = ReservaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ReservaFilter
    filterset_fields = ['estado', 'cliente', 'habitacion']
    search_fields = ['estado', 'cliente__nombre', 'habitacion__tipo']

    @extend_schema(
        parameters=[
            OpenApiParameter(name='fecha_inicio', location=OpenApiParameter.QUERY, description="Fecha mínima (YYYY-MM-DD)", type=str),
            OpenApiParameter(name='fecha_fin', location=OpenApiParameter.QUERY, description="Fecha máxima (YYYY-MM-DD)", type=str),
            OpenApiParameter(name='estado', location=OpenApiParameter.QUERY, description="Estado de la reserva", type=str),
            OpenApiParameter(name='cliente', location=OpenApiParameter.QUERY, description="ID del cliente", type=int),
            OpenApiParameter(name='habitacion', location=OpenApiParameter.QUERY, description="ID de la habitación", type=int),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        #tipo_pago = self.request.data.get('tipo_pago', 'Efectivo')
        reserva = serializer.save()

        # # Crear el pago automáticamente
        # pago = Pago.objects.create(
        #     monto=reserva.habitacion.precio,
        #     tipo_pago=tipo_pago,
        #     estado='exitoso'
        # )

        # reserva.pago = pago
        # reserva.save()

        # Marcar habitación como ocupada
        habitacion = reserva.habitacion
        habitacion.estado = 'ocupada'
        habitacion.save()

        # Enviar correo de notificación
        # send_mail(
        #     subject='Confirmación de reserva y pago',
        #     message=f'Se ha registrado una reserva para la habitación "{reserva.habitacion}" '
        #             f'del {reserva.fecha_inicio} al {reserva.fecha_fin}.\n'
        #             f'Monto: ${pago.monto} - Tipo de pago: {pago.tipo_pago}',
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=['jloorm2003@gmail.com', 'jloorm4@gmail.com'],
        #     fail_silently=True,
        # )

    def perform_destroy(self, instance):
        habitacion = instance.habitacion
        instance.delete()
        habitacion.estado = 'disponible'
        habitacion.save()

    @action(detail=True, methods=['post'])
    def checkin(self, request, pk=None):
        reserva = self.get_object()
        if reserva.estado != 'pendiente':
            return Response({'error': 'Solo se puede hacer check-in si la reserva está pendiente.'},
                            status=status.HTTP_400_BAD_REQUEST)

        reserva.estado = 'activa'
        reserva.save()
        reserva.habitacion.estado = 'ocupada'
        reserva.habitacion.save()
        return Response({'mensaje': 'Check-in realizado correctamente.'})

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        reserva = self.get_object()
        if reserva.estado != 'activa':
            return Response({'error': 'Solo se puede hacer check-out si la reserva está activa.'},
                            status=status.HTTP_400_BAD_REQUEST)

        reserva.estado = 'finalizada'
        reserva.save()
        reserva.habitacion.estado = 'disponible'
        reserva.habitacion.save()
        return Response({'mensaje': 'Check-out realizado correctamente.'})
