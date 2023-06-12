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
        return (
            request.user.is_authenticated
            and (
                request.user.is_user
                or request.user.is_admin
            )
        )


class IsAdmin(BasePermission):
    """Проверка, что пользователь админ или суперюзер."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class UserPermissions(BasePermission):

    def has_permission(self, request, view):

        if view.action in ['create', 'retrieve', 'list']:
            return True

        elif view.action in [
            'retrieve', 'update', 'partial_update', 'destroy'
        ]:
            return request.user.is_authenticated

        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ['retrieve', 'list']:
            return True

        if view.action == 'destroy':
            return (
                request.user.is_admin
                or obj == request.user
            )

        return False
