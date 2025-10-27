import django_filters
from .models import Reserva

class ReservaFilter(django_filters.FilterSet):
    fecha_inicio = django_filters.DateFilter(field_name='fecha_inicio', lookup_expr='gte')
    fecha_fin = django_filters.DateFilter(field_name='fecha_fin', lookup_expr='lte')
    estado = django_filters.CharFilter(field_name='estado', lookup_expr='icontains')
    cliente = django_filters.NumberFilter(field_name='cliente')  # si quieres buscar por ID
    habitacion = django_filters.NumberFilter(field_name='habitacion')  # si buscas por ID

    class Meta:
        model = Reserva
        fields = ['fecha_inicio', 'fecha_fin', 'estado', 'cliente', 'habitacion']
