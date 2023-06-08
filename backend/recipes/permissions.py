from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Проверка, что пользователь админ или суперюзер."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return request.method in SAFE_METHODS

        return (request.method in SAFE_METHODS
                or request.user.is_admin)


class IsAdminOrUser(BasePermission):
    """Проверка, что пользователь админ, суперюзер или авторизован"""

    def has_permission(self, request, view):
        return request.user and (
            request.user.is_user
            or request.user.is_admin
        )


class IsAdmin(BasePermission):
    """Проверка, что пользователь админ или суперюзер."""

    def has_permission(self, request, view):
        return request.user and request.user.is_admin
