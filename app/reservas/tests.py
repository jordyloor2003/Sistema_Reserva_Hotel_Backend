from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from datetime import date, timedelta

from app.clientes.models import Cliente
from app.habitaciones.models import Habitacion
from app.reservas.models import Reserva
from app.pagos.models import Pago
from rest_framework.authtoken.models import Token
from app.usuarios.models import Usuario

class ReservaAPITestCase(APITestCase):
    def setUp(self):
        # Crear usuario para autenticación
        self.usuario = Usuario.objects.create_user(
            username='testuser', password='testpass'
        )
        self.token = Token.objects.create(user=self.usuario)
        
        # Configurar token en cabecera Authorization para todas las peticiones
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.cliente = Cliente.objects.create(
            nombre='Test Cliente',
            documento='99999999',
            email='test@correo.com',
            telefono='123456789'
        )
        self.habitacion = Habitacion.objects.create(
            tipo='Doble',
            estado='disponible',
            precio=150.00
        )
        self.reserva_url = reverse('reserva-list')

    @patch('reservas.views.send_mail')
    def test_crear_reserva_exitosa(self, mock_send_mail):
        fecha_inicio = date.today() + timedelta(days=1)
        fecha_fin = date.today() + timedelta(days=3)

        data = {
            'cliente': self.cliente.id,
            'habitacion': self.habitacion.id,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'tipo_pago': 'Tarjeta'
        }
        response = self.client.post(self.reserva_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        reserva = Reserva.objects.first()
        self.assertIsNotNone(reserva.pago)
        self.assertEqual(reserva.pago.tipo_pago, 'Tarjeta')
        self.assertEqual(reserva.estado, 'pendiente')
        mock_send_mail.assert_called_once()

    def test_crear_reserva_con_fecha_pasada(self):
        data = {
            'cliente': self.cliente.id,
            'habitacion': self.habitacion.id,
            'fecha_inicio': date.today() - timedelta(days=2),
            'fecha_fin': date.today() + timedelta(days=1),
            'tipo_pago': 'Efectivo'
        }
        response = self.client.post(self.reserva_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crear_reserva_con_fecha_fin_antes(self):
        data = {
            'cliente': self.cliente.id,
            'habitacion': self.habitacion.id,
            'fecha_inicio': date.today() + timedelta(days=5),
            'fecha_fin': date.today() + timedelta(days=3),
            'tipo_pago': 'Efectivo'
        }
        response = self.client.post(self.reserva_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crear_reserva_habitacion_no_disponible(self):
        self.habitacion.estado = 'ocupada'
        self.habitacion.save()

        data = {
            'cliente': self.cliente.id,
            'habitacion': self.habitacion.id,
            'fecha_inicio': date.today() + timedelta(days=2),
            'fecha_fin': date.today() + timedelta(days=4),
        }
        response = self.client.post(self.reserva_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('reservas.views.send_mail')
    def test_eliminar_reserva_libera_habitacion(self, _):
        fecha_inicio = date.today() + timedelta(days=1)
        fecha_fin = date.today() + timedelta(days=3)
        reserva = Reserva.objects.create(
            cliente=self.cliente,
            habitacion=self.habitacion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='pendiente'
        )
        self.habitacion.estado = 'ocupada'
        self.habitacion.save()
        url = reverse('reserva-detail', args=[reserva.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.habitacion.refresh_from_db()
        self.assertEqual(self.habitacion.estado, 'disponible')

    @patch('reservas.views.send_mail')
    def test_checkin_reserva(self, _):
        reserva = Reserva.objects.create(
            cliente=self.cliente,
            habitacion=self.habitacion,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=1),
            estado='pendiente'
        )
        url = reverse('reserva-checkin', args=[reserva.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'activa')

    def test_checkin_no_valido(self):
        reserva = Reserva.objects.create(
            cliente=self.cliente,
            habitacion=self.habitacion,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=1),
            estado='activa'
        )
        url = reverse('reserva-checkin', args=[reserva.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_valido(self):
        reserva = Reserva.objects.create(
            cliente=self.cliente,
            habitacion=self.habitacion,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=1),
            estado='activa'
        )
        self.habitacion.estado = 'ocupada'
        self.habitacion.save()
        url = reverse('reserva-checkout', args=[reserva.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'finalizada')
        self.habitacion.refresh_from_db()
        self.assertEqual(self.habitacion.estado, 'disponible')

    def test_checkout_no_valido(self):
        reserva = Reserva.objects.create(
            cliente=self.cliente,
            habitacion=self.habitacion,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=1),
            estado='pendiente'
        )
        url = reverse('reserva-checkout', args=[reserva.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
