from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum

from users.permissions import IsAdminOrReadOnly

from .serializers import (
    TagSerializer,
    FavoriteSerializer,
    GetRecipeSerializer,
    IngredientSerializer,
    ShoppingCartSerializer,
    GetShortRecipeSerializer,
    CreateUpdateRecipeSerializer,
)
from .models import (
    Tag,
    Recipe,
    Ingredient,
    FavoriteRecipe,
    RecipesIngredients,
    ShoppingCartRecipe,
)
from .permissions import RecipePermissions
from .filters import RecipeFilter


class RecipeViewset(ModelViewSet):
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    serializer_classes = {
        'GET': GetRecipeSerializer,
        'POST': CreateUpdateRecipeSerializer,
        'PATCH': CreateUpdateRecipeSerializer,
        'DELETE': CreateUpdateRecipeSerializer
    }
    pagination_class = LimitOffsetPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        return self.serializer_classes.get(self.request.method)

    def get_permissions(self):
        if self.action in [
            'add_to_favorite', 'del_favorite',
            'add_to_shopping_cart', 'del_shopping_cart',
            'download_shopping_cart'
        ]:
            permission_classes = (IsAuthenticated,)
        else:
            permission_classes = (RecipePermissions,)

        return [permission() for permission in permission_classes]

    @action(
        detail=False,
        methods=['post'],
        url_path='favorite'
    )
    def add_to_favorite(self, request, id):
        """Добавление рецепта в избранное."""

        recipe = get_object_or_404(Recipe, id=id)
        serializer = FavoriteSerializer(
            context={'request': request},
            data={'id': id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            GetShortRecipeSerializer().to_representation(instance=recipe),
            status=status.HTTP_201_CREATED
        )

    @add_to_favorite.mapping.delete
    def del_favorite(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        user = request.user

        try:
            FavoriteRecipe.objects.filter(
                user=user, recipe=recipe).delete()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=['post']
    )
    def add_to_shopping_cart(self, request, id):
        """Добавление рецепта в список покупок."""

        recipe = get_object_or_404(Recipe, id=id)
        serializer = ShoppingCartSerializer(
            context={'request': request},
            data={'id': id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            GetShortRecipeSerializer().to_representation(instance=recipe),
            status=status.HTTP_201_CREATED
        )

    @add_to_shopping_cart.mapping.delete
    def del_shopping_cart(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        user = request.user

        try:
            ShoppingCartRecipe.objects.filter(
                user=user, recipe=recipe).delete()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        user = request.user
        filename = (f'{user.username}_shopping list') + '.txt'
        purchases = f'Список покупок для: {user.username}\n\n'
        ingredients = RecipesIngredients.objects.filter(
            recipe_shopping_cart_user=request.user
        ).values(
            'ingredient_name', 'ingredient_measurement_unit'
        ).annotate(amount=Sum('amount'))
        for num, i in enumerate(ingredients):
            purchases += (
                f"\n{i['ingredient_name']} - "
                f"{i['amount']} {i['ingredient_measurement_unit']}"
            )
            if num < ingredients.count() - 1:
                purchases += ', '
        response = HttpResponse(
            purchases, content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
