from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Habitacion
from app.reservas.models import Reserva
from datetime import date, timedelta
from app.clientes.models import Cliente
from app.usuarios.models import Usuario
from rest_framework.authtoken.models import Token

class HabitacionAPITestCase(APITestCase):
    def setUp(self):
        # Crear usuario admin y autenticar
        self.admin = Usuario.objects.create_user(
            username='admin',
            password='adminpass',
            rol='administrador',
            is_staff=True,
            is_superuser=True
        )
        self.token = Token.objects.create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.habitacion = Habitacion.objects.create(
            tipo='Suite',
            estado='disponible',
            precio=100.00
        )
        self.url_base = reverse('habitacion-list')

    def test_listar_habitaciones(self):
        response = self.client.get(self.url_base)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

        # Extra 1: buscar por tipo
        response = self.client.get(f"{self.url_base}?search=Suite")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Extra 2: buscar por estado
        response = self.client.get(f"{self.url_base}?search=disponible")
        self.assertEqual(len(response.data), 1)

    def test_crear_habitacion(self):
        data = {
            'tipo': 'Doble',
            'estado': 'ocupada',
            'precio': 80.00
        }
        response = self.client.post(self.url_base, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Extra 1: tipo vacío
        data['tipo'] = ''
        response = self.client.post(self.url_base, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Extra 2: estado inválido
        data['tipo'] = 'Simple'
        data['estado'] = 'reparación'
        response = self.client.post(self.url_base, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_actualizar_habitacion(self):
        url = reverse('habitacion-detail', args=[self.habitacion.id])
        data = {'estado': 'mantenimiento'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habitacion.refresh_from_db()
        self.assertEqual(self.habitacion.estado, 'mantenimiento')

        # Extra 1: cambiar precio a decimal negativo (opcional validación futura)
        response = self.client.patch(url, {'precio': -10}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # actualmente no hay validación en el modelo

        # Extra 2: actualizar con campos vacíos
        response = self.client.patch(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_eliminar_habitacion_sin_reservas(self):
        url = reverse('habitacion-detail', args=[self.habitacion.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_eliminar_habitacion_con_reserva_activa(self):
        cliente = Cliente.objects.create(
            nombre='Cliente de prueba',
            documento='00009999',
            email='cliente@prueba.com',
            telefono='9999999'
        )

        Reserva.objects.create(
            habitacion=self.habitacion,
            cliente=cliente,  # ← usamos el cliente creado
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=2),
            estado='activa'
        )

        url = reverse('habitacion-detail', args=[self.habitacion.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_disponibles_ok(self):
        url = reverse('habitacion-disponibles')
        fecha_inicio = (date.today() + timedelta(days=5)).strftime('%Y-%m-%d')
        fecha_fin = (date.today() + timedelta(days=10)).strftime('%Y-%m-%d')

        response = self.client.get(url, {'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_disponibles_fechas_invalidas(self):
        url = reverse('habitacion-disponibles')
        
        # Extra 1: faltan parámetros
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Extra 2: fechas en formato incorrecto
        response = self.client.get(url, {'fecha_inicio': '2024/01/01', 'fecha_fin': '2024-01-05'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
