from rest_framework import permissions

ROLES = ('admin', 'moderator')


class IsAdminOrReadOnlyPermission(permissions.BasePermission):
    """
    Разрешение, предоставляющее доступ к объекту только администратору,
    либо другому пользователю только для чтения.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.role == ROLES[0])

    def has_object_permission(self, request, view, obj):
        return (
            # request.method in permissions.SAFE_METHODS
            # or request.user.is_authenticated and request.user.is_staff()
            request.user.is_authenticated and request.user.role == ROLES[0]

        )


class IsAdminOnlyPermission(permissions.BasePermission):
    """
    Разрешение, предоставляющее доступ к объекту только администратору.
    """
    def has_permission(self, request, view):
        # return request.user.is_authenticated and request.user.is_staff()
        return request.user.is_authenticated and request.user.role == ROLES[0]


class RolesPermission(permissions.BasePermission):
    """
    Разрешение, позволяющее изменять объект модератору,
    администратору или самому владельцу.
    """
    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.method in permissions.SAFE_METHODS
            # or request.user.is_authenticated and request.user.is_staff()
            # or request.user.is_authenticated and request.user.role == ROLES[0]
            or request.user.is_authenticated and request.user.role in ROLES
        )
