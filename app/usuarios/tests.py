from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Usuario
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group

class UsuarioAPITestCase(APITestCase):
    def setUp(self):
        Group.objects.get_or_create(name='administrador')
        self.admin = Usuario.objects.create_user(
            username='admin',
            password='adminpass',
            email='admin@example.com',
            rol='administrador',
        )
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()

        self.token = Token.objects.create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.base_url = reverse('usuario-list')

    def test_listar_usuarios(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

        # Búsqueda por nombre
        response = self.client.get(f'{self.base_url}?search=admin')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Búsqueda por email
        response = self.client.get(f'{self.base_url}?search=admin@example.com')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_usuario(self):
        data = {
            'username': 'nuevo_user',
            'password': 'pass12345',
            'email': 'nuevo@test.com',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'rol': 'recepcionista'
        }
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Rol inválido
        data['rol'] = 'invalido'
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Sin username
        data['rol'] = 'gerente'
        data['username'] = ''
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_actualizar_usuario(self):
        url = reverse('usuario-detail', args=[self.admin.id])
        response = self.client.patch(url, {'first_name': 'Modificado'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.first_name, 'Modificado')

        # Actualización sin datos
        response = self.client.patch(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Email inválido
        response = self.client.patch(url, {'email': 'noesemail'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_eliminar_usuario(self):
        url = reverse('usuario-detail', args=[self.admin.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_restriccion_permiso_creacion_por_no_admin(self):
        # Crear usuario recepcionista sin permisos admin
        recepcionista = Usuario.objects.create(
            username='recep',
            rol='recepcionista',
            is_staff=True,
            is_superuser=False,
        )
        recepcionista.set_password('1234')
        recepcionista.save()

        token = Token.objects.create(user=recepcionista)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        data = {
            'username': 'otro_user',
            'password': '1234',
            'email': 'otro@test.com',
            'rol': 'gerente'
        }
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Actualización bloqueada también
        url = reverse('usuario-detail', args=[self.admin.id])
        response = self.client.patch(url, {'first_name': 'Denegado'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
