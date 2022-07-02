import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Amount, Ingredient, Recipe, Tag
from .validators import validate_amount, validate_cooking_time


class Base64ToImage(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        # data:image/png;base64,iVBORw0KGg
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        return ContentFile(base64.b64decode(imgstr), name='temp.' + ext)


class AmountSerializerPOST(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(write_only=True,
                                            source='ingredient_id',
                                            queryset=Ingredient.objects.all()
                                            )
    amount = serializers.IntegerField(validators=[validate_amount])

    class Meta:
        model = Amount
        fields = ('id', 'amount')


def set_amounts_tags(recipe, ingredients, tags):
    Amount.objects.bulk_create(
        [Amount(
            recipe_id=recipe,
            ingredient_id=ingredient['ingredient_id'],
            amount=ingredient['amount'])
            for ingredient in ingredients]
    )
    recipe.tags.set(tags)
    return recipe


class RecipeSerializerPOST(serializers.ModelSerializer):
    ingredients = AmountSerializerPOST(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all()
                                              )
    cooking_time = serializers.IntegerField(validators=[validate_cooking_time])
    image = Base64ToImage()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time',
                  'author')
        read_only_fields = ('author',)

    def validate_ingredients(self, value):
        if len(value) < 1:
            raise serializers.ValidationError('Нет ингредиентов в рецепте')
        recipe_ingredients = set()
        for ingredient in value:
            if ingredient['ingredient_id'] in recipe_ingredients:
                raise serializers.ValidationError(
                    'Ингредиент повторяется в рецепте')
            recipe_ingredients.add(ingredient['ingredient_id'])
        return value

    def validate_tags(self, value):
        if len(value) < 1:
            raise serializers.ValidationError('Рецепт должен иметь тэг')
        tags = set()
        for tag in value:
            if tag in tags:
                raise serializers.ValidationError(
                    'Теги не должны повторяться')
            tags.add(tag)
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        author = validated_data.pop('author')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(author=author, **validated_data)
        return set_amounts_tags(recipe, ingredients, tags)

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.image = validated_data.pop('image')
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        instance.cooking_time = validated_data.pop('cooking_time')

        instance.save()
        Amount.objects.filter(recipe_id=instance).delete()
        return set_amounts_tags(recipe=instance, ingredients=ingredients,
                                tags=tags)
