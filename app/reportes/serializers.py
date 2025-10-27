from rest_framework import serializers
from .models import Reporte
from app.usuarios.models import Usuario
from app.usuarios.serializers import UsuarioSerializer

class ReporteSerializer(serializers.ModelSerializer):
    # Solo lectura: se muestra el objeto Usuario completo
    usuario_detalle = UsuarioSerializer(source='usuario', read_only=True)
    
    # Solo escritura: se envía el ID del usuario
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    class Meta:
        model = Reporte
        fields = ['id', 'tipo', 'fecha_reporte', 'usuario', 'usuario_detalle']