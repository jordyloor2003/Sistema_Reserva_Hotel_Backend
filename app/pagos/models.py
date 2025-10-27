from django.db import models

class Pago(models.Model):
    TIPO_PAGO_CHOICES = [
    ('Efectivo', 'Efectivo'),
    ('Tarjeta', 'Tarjeta'),
    ('Transferencia', 'Transferencia'),
    ]

    ESTADO_CHOICES = [
        ('exitoso', 'Exitoso'),
        ('pendiente', 'Pendiente'),
        ('fallido', 'Fallido'),
    ]

    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    tipo_pago = models.CharField(max_length=50, choices=TIPO_PAGO_CHOICES, default='Efectivo')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='exitoso')

    def __str__(self):
        return f'Pago #{self.id} - {self.tipo_pago} - {self.estado}'
