from django.db import models
from app.usuarios.models import Usuario

class Reporte(models.Model):
    tipo = models.CharField(max_length=50)
    fecha_reporte = models.DateField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tipo} - {self.fecha_reporte}'
