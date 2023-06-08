from rest_framework.serializers import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from users.models import CustomUser as User
from .serializers import (
    TagSerializer,
    RecipeSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    ShoppingCartSerializer
)
from .models import (
    Recipe, FavoriteRecipe, ShoppingCartRecipe, Tag, Ingredient)
from .permissions import IsAdminOrReadOnly


class RecipeViewset(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (AllowAny,)

    @action(
        detail=False,
        methods=['post'],
        url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def add_to_favorite(self, request, id):
        """Добавление рецепта в избранное."""

        user = User.objects.get(username=request.user)
        recipe = get_object_or_404(Recipe, id=id)

        if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError('Рецепт уже добавлен!')

        favorite = FavoriteRecipe.objects.create(user=user, recipe=recipe)

        return Response(
            FavoriteSerializer().to_representation(instance=favorite),
            status=status.HTTP_201_CREATED
        )

    @add_to_favorite.mapping.delete
    def del_favorite(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        user = request.user

        try:
            FavoriteRecipe.objects.filter(
                user=user, recipe=recipe).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['post'],
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def add_to_shopping_cart(self, request, id):
        user = User.objects.get(username=request.user)
        recipe = get_object_or_404(Recipe, id=id)

        if ShoppingCartRecipe.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError('Рецепт уже добавлен!')

        favorite = ShoppingCartRecipe.objects.create(user=user, recipe=recipe)

        return Response(
            ShoppingCartSerializer().to_representation(instance=favorite),
            status=status.HTTP_201_CREATED
        )

    @add_to_shopping_cart.mapping.delete
    def del_shopping_cart(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        user = request.user

        try:
            ShoppingCartRecipe.objects.filter(
                user=user, recipe=recipe).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        try:
            shopping_cart = ShoppingCartRecipe.objects.filter(user=request.user).all()
            shopping_list = {}
            for item in shopping_cart:
                for recipe_ingredient in item.recipe.recipe_ingredients.all():
                    name = recipe_ingredient.ingredient.name
                    measuring_unit = recipe_ingredient.ingredient.measurement_unit
                    amount = recipe_ingredient.amount
                    if name not in shopping_list:
                        shopping_list[name] = {
                            'name': name,
                            'measurement_unit': measuring_unit,
                            'amount': amount
                        }
                    else:
                        shopping_list[name]['amount'] += amount
            content = (
                [f'{item["name"]} ({item["measurement_unit"]}) '
                f'- {item["amount"]}\n'
                for item in shopping_list.values()]
            )
            filename = 'shopping_list.txt'
            response = HttpResponse(content, content_type='text/plain')
            response['Content-Disposition'] = (
                'attachment; filename={0}'.format(filename)
            )
            return response
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
