from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from app.pagos.models import Pago
from app.reservas.models import Reserva
from app.clientes.models import Cliente
from app.habitaciones.models import Habitacion
from datetime import date, timedelta
from app.usuarios.models import Usuario
from rest_framework.authtoken.models import Token

class PagoAPITestCase(APITestCase):
    def setUp(self):
        # Crear usuario administrador y token
        self.admin = Usuario.objects.create_user(
            username='admin',
            password='adminpass',
            rol='administrador',
            is_staff=True,
            is_superuser=True
        )
        self.token = Token.objects.create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.pago = Pago.objects.create(
            monto=150.00,
            tipo_pago='Efectivo',
            estado='exitoso'
        )
        self.url_base = reverse('pago-list')

    def test_listar_pagos(self):
        response = self.client.get(self.url_base)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

        # Extra 1: búsqueda por tipo_pago
        response = self.client.get(f'{self.url_base}?search=Efectivo')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

        # Extra 2: filtro por estado
        response = self.client.get(f'{self.url_base}?estado=exitoso')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_pago_valido(self):
        data = {
            'monto': 200.00,
            'tipo_pago': 'Tarjeta',
            'estado': 'pendiente'
        }
        response = self.client.post(self.url_base, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pago.objects.count(), 2)

    def test_crear_pago_invalido(self):
        # Extra 1: falta el monto
        data = {'tipo_pago': 'Efectivo', 'estado': 'exitoso'}
        response = self.client.post(self.url_base, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Extra 2: tipo de pago inválido
        data = {'monto': 100.00, 'tipo_pago': 'Cheque', 'estado': 'exitoso'}
        response = self.client.post(self.url_base, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Extra 3: estado inválido
        data = {'monto': 100.00, 'tipo_pago': 'Tarjeta', 'estado': 'fallando'}
        response = self.client.post(self.url_base, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_detalle_pago(self):
        url = reverse('pago-detail', args=[self.pago.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tipo_pago'], 'Efectivo')

    def test_actualizar_pago(self):
        url = reverse('pago-detail', args=[self.pago.id])
        response = self.client.patch(url, {'estado': 'pendiente'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pago.refresh_from_db()
        self.assertEqual(self.pago.estado, 'pendiente')

    def test_eliminar_pago(self):
        url = reverse('pago-detail', args=[self.pago.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Pago.objects.count(), 0)

    def test_pago_con_reserva_id(self):
        # Creamos cliente y habitación
        cliente = Cliente.objects.create(
            nombre='Cliente Test',
            documento='12312312',
            email='cliente@test.com',
            telefono='5555555'
        )
        habitacion = Habitacion.objects.create(
            tipo='Doble',
            estado='disponible',
            precio=90.00
        )

        # Asociamos el pago a una reserva
        reserva = Reserva.objects.create(
            cliente=cliente,
            habitacion=habitacion,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=1),
            estado='completada',
            pago=self.pago  # suponiendo que el modelo Reserva tiene ForeignKey a Pago
        )

        url = reverse('pago-detail', args=[self.pago.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reserva_id'], reserva.id)
