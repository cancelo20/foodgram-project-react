from rest_framework.permissions import BasePermission


class RecipePermissions(BasePermission):

    def has_permission(self, request, view):

        if view.action in ['retrieve', 'list']:
            return True

        elif view.action in ['create', 'destroy']:
            return request.user.is_authenticated

        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ['retrieve', 'list', 'update']:
            return True

        if view.action == 'destroy':
            return (
                request.user.is_admin
                or obj.author == request.user
            )

        return False


class RecipeUpdatePermission(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_admin
            or obj.author == request.user
        )
