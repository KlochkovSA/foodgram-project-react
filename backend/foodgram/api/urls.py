from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CreateDeleteSubscription, IngredientViewSet,
                    ListSubscriptions, RecipeViewSet, TagViewSet,
                    download_shopping_cart, favorite, shopping_cart)

app_name = 'api'

router = SimpleRouter()
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)


urlpatterns = [
    path('users/subscriptions/', ListSubscriptions.as_view(),
         name='list_subscriptions'),
    path('users/<int:pk>/subscribe/',
         CreateDeleteSubscription.as_view(), name='subscribe'),
    path('recipes/<int:pk>/favorite/', favorite, name='favorite'),
    path('recipes/<int:pk>/shopping_cart/',
         shopping_cart,
         name='shopping_cart'),
    path('recipes/download_shopping_cart/',
         download_shopping_cart,
         name='download_shopping_cart'),
    path('', include(router.urls)),
]
