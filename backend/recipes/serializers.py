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
        read_only=True,
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = RecipesIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализация Рецептов."""

    author = AuthorSerializer(read_only=True)
    # tags = TagSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )

    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredient'
    )
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

    def create(self, validated_data):
        context = self.context.get('request')
        validated_data.pop('recipe_ingredient')

        try:
            recipe = Recipe.objects.create(
                **validated_data,
                author=self.context.get('request').user
            )
        except IntegrityError:
            pass

        tags_set = context.data.get('tags')

        for tag in tags_set:
            RecipesTags.objects.create(
                recipe=recipe,
                tag=Tag.objects.get(id=tag)
            )

        ingredients_set = context.data.get('ingredients')

        for ingredient in ingredients_set:
            ingredient_model = Ingredient.objects.get(id=ingredient['id'])
            RecipesIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient_model,
                amount=ingredient['amount'],
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

        RecipesIngredients.objects.filter(recipe=instance).delete()

        for ingredient in context.data.get('ingredients'):
            ingredient_model = Ingredient.objects.get(id=ingredient['id'])
            RecipesIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient_model,
                amount=ingredient['amount']
            )

        for tag_id in context.data.get('tags'):
            tag_model = Tag.objects.get(id=tag_id)
            RecipesTags.objects.update_or_create(
                recipe=recipe,
                tag=tag_model
            )

        return instance

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

        if username == recipe.author:
            raise ValidationError('Вы автор рецепта!')

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

        if username == recipe.author:
            raise ValidationError('Вы автор рецепта!')

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
