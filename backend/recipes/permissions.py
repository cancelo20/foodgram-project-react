from rest_framework.permissions import BasePermission


class RecipePermissions(BasePermission):

    def has_permission(self, request, view):

        if view.action in ['retrieve', 'list']:
            return True

        elif view.action in ['create', 'destroy', 'update']:
            return request.user.is_authenticated

        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ['retrieve', 'list']:
            return True

        if view.action in ['destroy', 'update']:
            return (
                request.user.is_admin
                or obj.author == request.user
            )

        return False
