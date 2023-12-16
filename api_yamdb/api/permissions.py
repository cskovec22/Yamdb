from rest_framework import permissions


roles = ('admin', 'moderator')


class RolesPermission(permissions.BasePermission):
    """
    Разрешение, позволяющее изменять объект модератору,
    администратору или самому владельцу.
    """
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.role in roles)


class IsAdminPermission(permissions.BasePermission):
    """Разрешение, позволяющее изменять объект только администратору."""
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin'
