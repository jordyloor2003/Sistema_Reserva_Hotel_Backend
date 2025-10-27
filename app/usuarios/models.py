# usuarios/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import Group

class Usuario(AbstractUser):
    ROLES = (
        ('administrador', 'Administrador'),
        ('recepcionista', 'Recepcionista'),
        ('gerente', 'Gerente'),
    )
    rol = models.CharField(max_length=20, choices=ROLES)

    def save(self, *args, **kwargs):
        # Asignación automática de permisos
        if self.rol == 'administrador':
            self.is_staff = True
            self.is_superuser = True
        elif self.rol in ['recepcionista', 'gerente']:
            self.is_staff = True
            self.is_superuser = False

        # Guardar el usuario
        super().save(*args, **kwargs)

        # Asignar grupo correspondiente
        if self.rol:
            try:
                grupo = Group.objects.get(name=self.rol)
                self.groups.set([grupo])
            except Group.DoesNotExist:
                pass