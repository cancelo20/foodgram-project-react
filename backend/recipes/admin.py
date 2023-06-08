from django.contrib import admin

from .models import(
    Recipe, RecipesTags, RecipesIngredients,
    Tag, Ingredient, FavoriteRecipe, ShoppingCartRecipe
)

admin.site.register(RecipesIngredients)
admin.site.register(ShoppingCartRecipe)
admin.site.register(FavoriteRecipe)
admin.site.register(RecipesTags)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Tag)
