from rest_framework import permissions


class IsAdminObjectReadOnlyPermission(permissions.BasePermission):
    """
    Разрешение, предоставляющее доступ к объекту только администратору.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnlyPermission(permissions.BasePermission):
    """
    Разрешение, позволяющее изменять объект только администратору,
    доступ остальным пользователям - только для чтения.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOnlyPermission(permissions.BasePermission):
    """
    Разрешение, предоставляющее доступ только администратору.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_admin


class RolesPermission(permissions.BasePermission):
    """
    Разрешение, позволяющее изменять объект модератору,
    администратору или самому владельцу.
    """

    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_admin or request.user.is_moderator)
        )
