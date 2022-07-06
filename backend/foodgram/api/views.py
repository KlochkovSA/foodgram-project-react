from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import Follow
from .filters import IngredientFilter, RecipeFilter
from .followSerializer import FollowSerializer
from .recipe_serializer_GET import RecipeSerializerGET
from .recipe_serializer_POST import RecipeSerializerPOST
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author').all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.select_related('author').all()
        if user.is_anonymous:
            return queryset
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_favorited:
            queryset = queryset.filter(in_favorite__user=user)
        if is_in_shopping_cart:
            return queryset.filter(in_shopping_cart__user=user)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeSerializerPOST
        return RecipeSerializerGET

    def create(self, request, *args, **kwargs):
        serializer = RecipeSerializerPOST(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save(author=self.request.user)
        serializer_context = {'request': request}
        response_data = RecipeSerializerGET(recipe,
                                            context=serializer_context).data
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if self.request.stream.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)

        recipe = serializer.save(author=self.request.user)
        serializer_context = {'request': request}
        response_data = RecipeSerializerGET(recipe,
                                            context=serializer_context).data
        return Response(response_data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class CreateDeleteSubscription(generics.CreateAPIView,
                               generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()

    def create(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = request.user
        author = get_object_or_404(User, pk=pk)
        Follow.objects.create(user=user, author=author)
        serializer_context = {'request': request}
        serializer = FollowSerializer(author, context=serializer_context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        pk = kwargs.get('pk')
        user = request.user
        author = get_object_or_404(User, pk=pk)
        follow = get_object_or_404(Follow, user=user, author=author)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListSubscriptions(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FollowSerializer

    def get_queryset(self):
        return User.objects.filter(followers__user=self.request.user)


def create_or_delete(model, request, pk):
    user = request.user
    recipe = get_object_or_404(Recipe, pk=pk)
    flag = model.objects.filter(user=user,
                                recipe=recipe).exists()
    if request.method == 'POST' and not flag:
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE' and flag:
        item = get_object_or_404(model, user=user,
                                 recipe=recipe)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@permission_classes([permissions.IsAuthenticated])
@api_view(['POST', 'DELETE'])
def favorite(request, pk):
    return create_or_delete(FavoriteRecipe, request, pk)


@permission_classes([permissions.IsAuthenticated])
@api_view(['POST', 'DELETE'])
def shopping_cart(request, pk):
    return create_or_delete(ShoppingCart, request, pk)
