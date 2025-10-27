from django.db import models

class Habitacion(models.Model):
    ESTADOS_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    
    tipo = models.CharField(max_length=50)
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES)
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f'Habitación {self.id} - {self.tipo}'
