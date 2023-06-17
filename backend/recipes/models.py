from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser as User


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тэгов."""

    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('Цвет тэга', max_length=7, unique=True)
    slug = models.SlugField(max_length=10, unique=True)

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['slug'],
                name='unique_slug'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField('Название', max_length=200)
    text = models.TextField('Описание рецепта')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        help_text='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipesIngredients'
    )
    tags = models.ManyToManyField(
        Tag, through='RecipesTags',
    )
    image = models.ImageField('Изображение', upload_to='recipes/')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(
                1, 'Минимальное время - 1 минута'
            )
        ],
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name


class RecipesIngredients(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиентов',
        default=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]


class RecipesTags(models.Model):
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, related_name='recipe_tag')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_tag')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag'
            )
        ]


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='favorite_recipes'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite'
            )
        ]


class ShoppingCartRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipes'
    )

    class Meta:
        verbose_name = 'Shopping cart'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_cart'
            )
        ]
