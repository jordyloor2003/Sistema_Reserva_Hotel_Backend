from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Cliente
from app.usuarios.models import Usuario
from rest_framework.authtoken.models import Token

class ClienteAPITestCase(APITestCase):
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

        # Crear un cliente para pruebas
        self.cliente = Cliente.objects.create(
            nombre='Juan Pérez',
            documento='12345678',
            email='juan@example.com',
            telefono='5551234'
        )
        self.url_base = reverse('cliente-list')

    def test_listar_clientes(self):
        response = self.client.get(self.url_base)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Caso extra 1: crear un segundo cliente y verificar lista
        Cliente.objects.create(nombre='Ana', documento='00001111', email='ana@example.com', telefono='0000')
        response = self.client.get(self.url_base)
        self.assertEqual(len(response.data), 2)

        # Caso extra 2: sin clientes
        Cliente.objects.all().delete()
        response = self.client.get(self.url_base)
        self.assertEqual(len(response.data), 0)

    def test_crear_cliente(self):
        data = {
            'nombre': 'Ana Gómez',
            'documento': '87654321',
            'email': 'ana@example.com',
            'telefono': '5556789'
        }
        response = self.client.post(self.url_base, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Extra 1: Faltan campos requeridos
        data_incompleto = {'nombre': 'FaltaDocYCorreo'}
        response = self.client.post(self.url_base, data_incompleto, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Extra 2: Email inválido
        data_mal_email = {
            'nombre': 'Mal Email',
            'documento': '123123',
            'email': 'no-es-email',
            'telefono': '123123'
        }
        response = self.client.post(self.url_base, data_mal_email, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_detalle_cliente(self):
        url = reverse('cliente-detail', args=[self.cliente.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('documento', response.data)
        self.assertEqual(response.data['documento'], '12345678')

        # Extra 1: ID no existente
        response_not_found = self.client.get(reverse('cliente-detail', args=[9999]))
        self.assertEqual(response_not_found.status_code, status.HTTP_404_NOT_FOUND)

        # Extra 2: Volver a pedir el cliente original y confirmar sus datos
        response = self.client.get(url)
        self.assertEqual(response.data['nombre'], 'Juan Pérez')
        self.assertEqual(response.data['email'], 'juan@example.com')


    def test_actualizar_cliente(self):
        url = reverse('cliente-detail', args=[self.cliente.id])
        data = {'nombre': 'Juan Actualizado'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Juan Actualizado')

        # Extra 1: Actualizar documento a uno existente (debe fallar)
        nuevo = Cliente.objects.create(nombre='Otro', documento='111222', email='otro@x.com', telefono='4444')
        data = {'documento': '12345678'}  # mismo del primero
        response = self.client.patch(reverse('cliente-detail', args=[nuevo.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Extra 2: Actualización con datos vacíos (no debería cambiar nada)
        response = self.client.patch(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_eliminar_cliente(self):
        url = reverse('cliente-detail', args=[self.cliente.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Extra 1: Eliminar cliente inexistente
        response = self.client.delete(url)  # ya fue borrado
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Extra 2: Verificar que ya no existe
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_documento_unico(self):
        data = {
            'nombre': 'Repetido',
            'documento': '12345678',  # ya existente
            'email': 'otro@example.com',
            'telefono': '9999999'
        }
        response = self.client.post(self.url_base, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Extra 1: documento único pero email duplicado
        data = {
            'nombre': 'Otro',
            'documento': '00009999',
            'email': 'juan@example.com',
            'telefono': '123'
        }
        response = self.client.post(self.url_base, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Extra 2: Crear cliente con otro documento y correo únicos
        data = {
            'nombre': 'Nuevo',
            'documento': 'nuevo123',
            'email': 'nuevo@example.com',
            'telefono': '555555'
        }
        response = self.client.post(self.url_base, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_busqueda_por_nombre(self):
        response = self.client.get(f"{self.url_base}?search=Juan")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

        # Extra 1: Búsqueda que no devuelve resultados
        response = self.client.get(f"{self.url_base}?search=NoExiste")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # Extra 2: Búsqueda por teléfono
        response = self.client.get(f"{self.url_base}?search=5551234")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['documento'], '12345678')
