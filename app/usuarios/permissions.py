from rest_framework import permissions

class IsAdministrador(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and (
                request.user.is_superuser or getattr(request.user, 'rol', None) == 'administrador'
            )
        )

class IsRecepcionista(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and getattr(request.user, 'rol', None) == 'recepcionista'
        )

class IsGerente(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and (
                request.user.is_superuser or getattr(request.user, 'rol', None) == 'gerente'
            )
        )
