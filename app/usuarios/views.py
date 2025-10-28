from rest_framework import viewsets, permissions, filters
from .models import Usuario
from .serializers import UsuarioSerializer
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

class IsAdminUserOnly(permissions.BasePermission):
    """
    Permite acceso solo a usuarios con rol 'administrador'.
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_superuser or getattr(user, 'rol', None) == 'administrador'))

@extend_schema(tags=['Usuarios'])
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().order_by('username')
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        if self.action == 'create':
            permission_classes = [AllowAny]
        return [perm() for perm in permission_classes]
