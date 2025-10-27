from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from app.usuarios.models import Usuario
from app.reservas.models import Reserva
from app.habitaciones.models import Habitacion
from app.clientes.models import Cliente
from app.pagos.models import Pago
from app.reportes.models import Reporte
from datetime import date, timedelta
from rest_framework.authtoken.models import Token

class ReporteAPITestCase(APITestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='admin', password='adminpass', rol='administrador'
        )
        self.token = Token.objects.create(user=self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Crear cliente, habitación, reserva y pago
        self.cliente = Cliente.objects.create(
            nombre='Cliente Prueba',
            documento='11111111',
            email='cliente@hotel.com',
            telefono='123456789'
        )
        self.habitacion = Habitacion.objects.create(
            tipo='Doble',
            estado='disponible',
            precio=120.00
        )
        self.reserva = Reserva.objects.create(
            cliente=self.cliente,
            habitacion=self.habitacion,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=2),
            estado='activa'
        )
        self.pago = Pago.objects.create(
            monto=200.00,
            tipo_pago='Tarjeta',
            estado='exitoso'
        )
        self.reserva.pago = self.pago
        self.reserva.save()

        self.reporte = Reporte.objects.create(
            tipo='Ingresos',
            fecha_reporte=date.today(),
            usuario=self.usuario
        )

    def test_reporte_reservas_sin_filtros(self):
        response = self.client.get('/api/reportes/reservas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_reporte_reservas_con_filtros(self):
        fecha = date.today().strftime('%Y-%m-%d')

        # Filtro por estado
        response = self.client.get('/api/reportes/reservas/', {'estado': 'activa'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Filtro por fechas
        response = self.client.get('/api/reportes/reservas/', {
            'fecha_inicio': fecha,
            'fecha_fin': fecha
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reporte_ingresos_sin_filtros(self):
        response = self.client.get('/api/reportes/ingresos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_general', response.data)
        self.assertIn('detalle_por_tipo', response.data)

    def test_reporte_ingresos_con_filtros(self):
        hoy = date.today().strftime('%Y-%m-%d')

        # Filtro por tipo de pago
        response = self.client.get('/api/reportes/ingresos/', {'tipo_pago': 'Tarjeta'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_general'], 200)

        # Filtro por fechas
        response = self.client.get('/api/reportes/ingresos/', {
            'fecha_inicio': hoy,
            'fecha_fin': hoy
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_reporte_con_usuario(self):
        response = self.client.post('/api/reportes/', {
            'tipo': 'Reservas',
            'fecha_reporte': date.today(),
            'usuario': self.usuario.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reporte.objects.count(), 2)

    def test_usuario_detalle_en_reporte(self):
        response = self.client.get(f'/api/reportes/{self.reporte.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('usuario_detalle', response.data)
