from rest_framework import serializers

from recepts.models import Amount, Ingredient, Recipe
from users.serializers import UserGetSerializer

from .serializers import TagSerializer


class AmountIngredientSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        return obj.amount


class RecipeSerializerGET(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'name', 'text', 'image', 'cooking_time')

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.all()
        for ingredient in ingredients:
            ingredient.amount = Amount.objects.get(ingredient_id=ingredient,
                                                   recipe_id=obj).amount
        serializer = AmountIngredientSerializer(ingredients, many=True)
        return serializer.data

    def get_author(self, obj):
        serializer_context = {'request': self.context.get('request')}
        author_serializer = UserGetSerializer(obj.author,
                                              context=serializer_context)
        return author_serializer.data
