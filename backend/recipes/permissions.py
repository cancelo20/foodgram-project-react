from rest_framework.permissions import BasePermission, SAFE_METHODS


class RecipePermissions(BasePermission):

    def has_permission(self, request, view):

        if view.action in ['retrieve', 'list']:
            return True

        elif view.action in ['create', 'destroy', 'update']:
            return request.user.is_authenticated

        elif request.method == 'PATCH':
            return request.user.is_authenticated

        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ['retrieve', 'list']:
            return True

        return (
            request.user.is_admin
            or obj.author == request.user
        )


class IsAuthorOrAdminPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and (
            request.user.is_admin
            or obj.author == request.user
            or request.method == 'POST'
        ):
            return True
        return request.method in SAFE_METHODS
