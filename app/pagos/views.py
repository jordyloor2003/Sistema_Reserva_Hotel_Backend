from rest_framework import viewsets, filters
from .models import Pago
from .serializers import PagoSerializer
from drf_spectacular.utils import extend_schema

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
