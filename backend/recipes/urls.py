from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import RecipeViewset, TagViewSet, IngredientsViewSet


router = DefaultRouter()
router.register(r'recipes', RecipeViewset)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientsViewSet)

favorite = RecipeViewset.as_view(
    {
        'post': 'add_to_favorite',
        'delete': 'del_favorite'
    }
)

shopping_cart = RecipeViewset.as_view(
    {
        'post': 'add_to_shopping_cart',
        'delete': 'del_shopping_cart'
    }
)

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/<int:id>/favorite/', favorite),
    path('recipes/<int:id>/shopping_cart/', shopping_cart)
]
