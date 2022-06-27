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

    def validated_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Убедитесь, что это значение больше либо равно 1.")

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

    def validated_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Убедитесь, что это значение больше либо равно 1.")

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        author = validated_data.pop('author')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(author=author, **validated_data)
        for ingredient in ingredients:
            Amount.objects.create(ingredient_id=ingredient['ingredient_id'],
                                  recipe_id=recipe,
                                  amount=ingredient['amount'])
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        image = validated_data.pop('image')
        name = validated_data.pop('name')
        text = validated_data.pop('text')
        cooking_time = validated_data.pop('cooking_time')

        instance.image = image
        instance.name = name
        instance.text = text
        instance.cooking_time = cooking_time

        instance.save()
        Amount.objects.filter(recipe_id=instance).delete()

        for ingredient in ingredients:
            Amount.objects.create(ingredient_id=ingredient['ingredient_id'],
                                  recipe_id=instance,
                                  amount=ingredient['amount'])
        instance.tags.set(tags)
        return instance
