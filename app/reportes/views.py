from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum
from app.reservas.models import Reserva
from app.pagos.models import Pago
from app.usuarios.permissions import IsAdministrador, IsGerente
from rest_framework import viewsets
from .models import Reporte
from .serializers import ReporteSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Reportes'])
class ReporteViewSet(viewsets.ModelViewSet):
    queryset = Reporte.objects.all()
    serializer_class = ReporteSerializer

class ReporteReservasView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdministrador | IsGerente]

    @extend_schema(tags=['Reportes'])
    def get(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        estado = request.query_params.get('estado')

        reservas = Reserva.objects.all()

        if fecha_inicio:
            reservas = reservas.filter(fecha_inicio__gte=fecha_inicio)
        if fecha_fin:
            reservas = reservas.filter(fecha_fin__lte=fecha_fin)
        if estado:
            reservas = reservas.filter(estado=estado)

        data = reservas.values(
            'cliente__nombre',
            'habitacion__tipo',
            'fecha_inicio',
            'fecha_fin',
            'estado'
        )

        return Response(list(data))


class ReporteIngresosView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdministrador | IsGerente]

    @extend_schema(tags=['Reportes'])
    def get(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        tipo_pago = request.query_params.get('tipo_pago')

        pagos = Pago.objects.all()

        if fecha_inicio:
            pagos = pagos.filter(fecha__date__gte=fecha_inicio)
        if fecha_fin:
            pagos = pagos.filter(fecha__date__lte=fecha_fin)
        if tipo_pago:
            pagos = pagos.filter(tipo_pago=tipo_pago)

        total = pagos.aggregate(total_ingresos=Sum('monto'))['total_ingresos'] or 0

        detalle = pagos.values('tipo_pago').annotate(total=Sum('monto'))

        return Response({
            "total_general": total,
            "detalle_por_tipo": list(detalle)
        })
