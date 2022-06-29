from rest_framework import serializers

from recepts.models import Ingredient, Recipe, Tag
from .recipe_serializer_POST import IngredientSerializerPOST


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'color', 'slug', 'name')


class IngredientSerializer(IngredientSerializerPOST):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
