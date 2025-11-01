from rest_framework import viewsets, filters
from .models import Pago
from .serializers import PagoSerializer
from drf_spectacular.utils import extend_schema
from app.reservas.models import Reserva

@extend_schema(tags=['Pagos'])
class PagoViewSet(viewsets.ModelViewSet):
    """
    API REST para gestionar pagos locales: efectivo, tarjeta, etc.
    """
    queryset = Pago.objects.all().order_by('-fecha')
    serializer_class = PagoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['tipo_pago', 'estado']
    filterset_fields = ['tipo_pago', 'estado']

    def perform_create(self, serializer):
        # Guarda el pago primero
        pago = serializer.save()
        # Verifica si el front envió una reserva_id
        reserva_id = self.request.data.get('reserva_id')
        if reserva_id:
            try:
                reserva = Reserva.objects.get(id=reserva_id)
                reserva.pago = pago
                reserva.save()
            except Reserva.DoesNotExist:
                pass