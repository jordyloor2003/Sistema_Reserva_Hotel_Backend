from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from .models import Habitacion
from .serializers import HabitacionSerializer
from app.reservas.models import Reserva 
from rest_framework.decorators import action
from datetime import datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_yasg import openapi

@extend_schema(tags=['Habitaciones'])
class HabitacionViewSet(viewsets.ModelViewSet):
    queryset = Habitacion.objects.all().order_by('tipo')
    serializer_class = HabitacionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['tipo', 'estado']

    def destroy(self, request, *args, **kwargs):
        habitacion = self.get_object()

        # Verificamos si tiene reservas activas o pendientes
        reservas = Reserva.objects.filter(
            habitacion=habitacion,
            estado__in=['pendiente', 'activa']
        )

        if reservas.exists():
            return Response(
                {'error': 'No se puede eliminar la habitación. Tiene reservas activas o pendientes.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().destroy(request, *args, **kwargs)
    
    @extend_schema(
        methods=['GET'],
        parameters=[
            OpenApiParameter(
                name='fecha inicio',
                location=OpenApiParameter.QUERY,
                description="yyyy-MM-dd",
                type=str,
                required=True
            ),
            OpenApiParameter(
                name='fecha_fin',
                location=OpenApiParameter.QUERY,
                description="yyyy-MM-dd",
                type=str,
                required=True
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='disponibles')
    def disponibles(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        if not fecha_inicio or not fecha_fin:
            return Response({'error': 'Debe proporcionar fecha_inicio y fecha_fin en formato YYYY-MM-DD'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        except ValueError:
            return Response({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Buscar habitaciones que NO tienen reservas que se solapen
        habitaciones_ocupadas = Reserva.objects.filter(
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
            estado__in=['pendiente', 'activa']
        ).values_list('habitacion_id', flat=True)

        disponibles = Habitacion.objects.exclude(id__in=habitaciones_ocupadas).filter(estado='disponible')

        serializer = self.get_serializer(disponibles, many=True)
        return Response(serializer.data)