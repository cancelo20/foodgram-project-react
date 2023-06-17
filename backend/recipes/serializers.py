from drf_extra_fields.fields import Base64ImageField

from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from django.db import IntegrityError

from users.models import CustomUser as User
from .models import (
    Ingredient, Recipe, Tag,
    RecipesIngredients, RecipesTags,
    FavoriteRecipe, ShoppingCartRecipe
)


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализация автора рецепта."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class TagSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipesIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')
        extra_kwargs = {
            'id': {'read_only': True},
            'name': {'read_only': True},
            'measurement_unit': {'read_only': True},
        }


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipesIngredients
        fields = ('id', 'amount')


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализация Get-запроса Рецептов."""

    author = AuthorSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField(
        max_length=None, use_url=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'is_favorited': {'read_only': True},
            'is_in_shopping_cart': {'read_only': True}
        }

    def get_ingredients(self, data):
        ingredients = RecipesIngredients.objects.filter(recipe=data)

        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, data):
        request = self.context.get('request')

        if request is None or request.user.is_anonymous:
            return False

        if FavoriteRecipe.objects.filter(
                recipe=data, user=request.user).exists():

            return True

        return False

    def get_is_in_shopping_cart(self, data):
        request = self.context.get('request')

        if request is None or request.user.is_anonymous:
            return False

        if ShoppingCartRecipe.objects.filter(
                recipe=data, user=request.user).exists():

            return True

        return False


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    """Сериализация создания/изменения Рецептов."""

    author = AuthorSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = CreateRecipeIngredientSerializer(many=True)
    image = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        context = self.context.get('request')
        validated_data.pop('tags')
        validated_data.pop('ingredients')

        try:
            recipe = Recipe.objects.create(
                **validated_data,
                author=self.context.get('request').user
            )
        except IntegrityError:
            pass

        for ingredient in context.data.get('ingredients'):
            RecipesIngredients.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient.get('id')),
                amount=ingredient['amount'],
            )

        for tag in context.data.get('tags'):
            RecipesTags.objects.create(
                recipe=recipe,
                tag=Tag.objects.get(id=tag.get('id'))
            )

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()

        context = self.context.get('request')
        recipe = instance

        validated_data.pop('recipe_ingredient')
        validated_data.pop('recipe_tag')

        RecipesIngredients.objects.filter(recipe=instance).delete()
        RecipesTags.objects.filter(recipe=instance).delete()

        for ingredient in context.data.get('ingredients'):
            RecipesIngredients.objects.update_or_create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient.get('id')),
                amount=ingredient.get('amount')
            )

        for tag in context.data.get('tags'):
            RecipesTags.objects.update_or_create(
                recipe=recipe,
                tag=Tag.objects.get(id=tag.get('id'))
            )

        return instance


class GetShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализация избранных рецептов."""

    id = serializers.IntegerField()

    class Meta:
        model = FavoriteRecipe
        fields = ('id',)

    def validate(self, data):
        username = self.context.get('request').user
        recipe = Recipe.objects.get(id=data.get('id'))

        if FavoriteRecipe.objects.filter(
                user=username, recipe=recipe).exists():
            raise ValidationError('Рецепт уже добавлен!')

        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        recipe = Recipe.objects.get(id=validated_data.get('id'))

        favorite = FavoriteRecipe.objects.create(user=user, recipe=recipe)
        favorite.save()

        return favorite


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализация списка покупок."""

    id = serializers.IntegerField()

    class Meta:
        model = ShoppingCartRecipe
        fields = ('id',)

    def validate(self, data):
        username = self.context.get('request').user
        recipe = Recipe.objects.get(id=data.get('id'))

        if ShoppingCartRecipe.objects.filter(
                user=username, recipe=recipe).exists():
            raise ValidationError('Рецепт уже добавлен!')

        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        recipe = Recipe.objects.get(id=validated_data.get('id'))

        favorite = ShoppingCartRecipe.objects.create(user=user, recipe=recipe)
        favorite.save()

        return favorite
