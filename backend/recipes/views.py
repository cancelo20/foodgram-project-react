from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from .serializers import (
    TagSerializer,
    RecipeSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    ShoppingCartSerializer,
    GetShortRecipeSerializer
)
from .models import (
    Recipe, FavoriteRecipe, ShoppingCartRecipe, Tag, Ingredient)

from .filters import IngredientFilter, RecipeFilter

from users.permissions import IsAdminOrReadOnly
from .permissions import RecipePermissions


class RecipeViewset(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

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
        methods=['GET'],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        try:
            shopping_cart = ShoppingCartRecipe.objects.filter(
                user=request.user).all()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            shopping_list = {}
            for item in shopping_cart:
                for recipe_ingredient in item.recipe.recipe_ingredients.all():
                    name = recipe_ingredient.ingredient.name
                    m_unit = recipe_ingredient.ingredient.measurement_unit
                    amount = recipe_ingredient.amount
                    if name not in shopping_list:
                        shopping_list[name] = {
                            'name': name,
                            'measurement_unit': m_unit,
                            'amount': amount
                        }
                    else:
                        shopping_list[name]['amount'] += amount
            content = (
                [
                    f'{item["name"]} ({item["measurement_unit"]}) '
                    f'- {item["amount"]}\n'
                    for item in shopping_list.values()
                ]
            )
            filename = 'shopping_list.txt'
            response = HttpResponse(content, content_type='text/plain')
            response['Content-Disposition'] = (
                'attachment; filename={0}'.format(filename)
            )
            return response


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = IngredientFilter
