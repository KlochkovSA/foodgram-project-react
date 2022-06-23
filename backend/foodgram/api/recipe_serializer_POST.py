import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recepts.models import Amount, Ingredient, Recipe, Tag


class Base64ToImage(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        # data:image/png;base64,iVBORw0KGg
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        return ContentFile(base64.b64decode(imgstr), name='temp.' + ext)


class IngredientSerializerPOST(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id',)


class AmountSerializerPOST(serializers.ModelSerializer):
    ingredient_id = IngredientSerializerPOST(read_only=True)
    id = serializers.PrimaryKeyRelatedField(write_only=True,
                                            source='ingredient_id',
                                            queryset=Ingredient.objects.all()
                                            )

    class Meta:
        model = Amount
        fields = ('id', 'amount', 'ingredient_id')


class RecipeSerializerPOST(serializers.ModelSerializer):
    ingredients = AmountSerializerPOST(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all()
                                              )
    image = Base64ToImage()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time',
                  'author')
        read_only_fields = ('author',)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        author = validated_data.pop('author')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(author=author, **validated_data)
        for ingredient in ingredients:
            Amount.objects.create(ingredient_id=ingredient['ingredient_id'],
                                  recipe_id=recipe,
                                  amount=ingredient['amount'])
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.update(**validated_data)
        for ingredient in ingredients:
            obj = ingredient['ingredient_id']
            Amount.objects.update_or_create(ingredient_id=obj,
                                            recipe_id=instance,
                                            amount=ingredient['amount'])
        for tag in tags:
            instance.tags.add(tag)
        return instance
