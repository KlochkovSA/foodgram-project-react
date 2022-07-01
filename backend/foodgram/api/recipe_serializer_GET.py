from rest_framework import serializers

from recipes.models import Amount, Ingredient, Recipe
from users.serializers import UserGetSerializer
from .serializers import TagSerializer


class AmountIngredientSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializerGET(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name', 'text',
                  'image', 'cooking_time')

    def get_author(self, obj):
        serializer_context = {'request': self.context.get('request')}
        author_serializer = UserGetSerializer(obj.author,
                                              context=serializer_context)
        return author_serializer.data

    def get_is_favorited(self, obj):
        request = self.context.get('request', None)
        if request.user.is_anonymous:
            return False
        return request.user.favorite_recipes.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request', None)
        if request.user.is_anonymous:
            return False
        return request.user.shopping_сart.filter(recipe=obj).exists()

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.all()
        for ingredient in ingredients:
            ingredient.amount = Amount.objects.get(ingredient_id=ingredient,
                                                   recipe_id=obj).amount
        serializer = AmountIngredientSerializer(ingredients, many=True)
        return serializer.data
