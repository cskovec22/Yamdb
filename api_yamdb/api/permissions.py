from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Пользователи могут просматривать объекты,
    но только администраторы могут создавать, редактировать или удалять их.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
