from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import (api_view, permission_classes,
                                       renderer_classes)
from rest_framework.response import Response

from recepts.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import Follow

from .followSerializer import FollowSerializer
from .recipe_serializer_GET import RecipeSerializerGET
from .recipe_serializer_POST import RecipeSerializerPOST
from .renderer import TextRenderer
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeSerializerPOST
        return RecipeSerializerGET

    def create(self, request, *args, **kwargs):
        serializer = RecipeSerializerPOST(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save(author=self.request.user)
        serializer_context = {'request': request}
        response_data = RecipeSerializerGET(recipe,
                                            context=serializer_context).data
        return Response(response_data, status=status.HTTP_201_CREATED)


@permission_classes([permissions.IsAuthenticated])
@api_view(['POST', 'DELETE'])
def subscribe(request, pk):
    user = request.user
    author = get_object_or_404(get_user_model(), pk=pk)
    if request.method == 'POST':
        Follow.objects.create(user=user, author=author)
        serializer_context = {'request': request}
        serializer = FollowSerializer(author, context=serializer_context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    follow = get_object_or_404(Follow, user=user, author=author)
    follow.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_subscriptions(request):
    followers = request.user.follower.all()
    authors = []
    for follow_obj in followers:
        author = follow_obj.author
        authors.append(author)
    serializer_context = {'request': request}
    serializer = FollowSerializer(authors, many=True,
                                  context=serializer_context)
    return Response(serializer.data)


@permission_classes([permissions.IsAuthenticated])
@api_view(['POST', 'DELETE'])
def favorite(request, pk):
    user = request.user
    recipe = get_object_or_404(Recipe, pk=pk)
    is_favourite_recipe = FavoriteRecipe.objects.filter(user=user,
                                                        recipe=recipe).exists()
    if request.method == 'POST' and not is_favourite_recipe:
        FavoriteRecipe.objects.create(user=user, recipe=recipe)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE' and is_favourite_recipe:
        favorite_recipe = get_object_or_404(FavoriteRecipe, user=user,
                                            recipe=recipe)
        favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@permission_classes([permissions.IsAuthenticated])
@api_view(['POST', 'DELETE'])
def shopping_cart(request, pk):
    user = request.user
    recipe = get_object_or_404(Recipe, pk=pk)
    is_in_shopping_cart = ShoppingCart.objects.filter(user=user,
                                                      recipe=recipe).exists()
    if request.method == 'POST' and not is_in_shopping_cart:
        ShoppingCart.objects.create(user=user, recipe=recipe)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE' and is_in_shopping_cart:
        favorite_recipe = get_object_or_404(ShoppingCart, user=user,
                                            recipe=recipe)
        favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@renderer_classes([TextRenderer])
def download_shopping_cart(request):
    user = request.user
    shopping_cart = ShoppingCart.objects.filter(user=user).all()
    result_dict = {}
    for item in shopping_cart:
        for ingredient_amount in item.recipe.amounts.all():
            ingredient_id = ingredient_amount.ingredient_id
            # ingredient_id gives us string representation
            # of Ingredient model object
            key = f'{ingredient_id} ({ingredient_id.measurement_unit})'
            # Фарш (баранина и говядина) (г) — 600
            # if hasattr(result, key):
            if key in result_dict:
                result_dict[key] += ingredient_amount.amount
                continue
            result_dict[key] = ingredient_amount.amount
    result = ''.join([f'{k} - {v}\n' for k, v in result_dict.items()])
    return Response(result,
                    headers={'Content-Disposition':
                             'attachment; filename="file.txt"'},
                    status=status.HTTP_200_OK,
                    content_type='text/plain')
