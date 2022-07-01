from django.contrib import admin

from .models import (Amount, FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                     Tag)


@admin.register(Amount)
class AmountAdmin(admin.ModelAdmin):
    list_display = ('ingredient_id', 'recipe_id', 'amount')


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'text', 'image', 'cooking_time', 'author',
                    'created', 'favourite_count')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    def favourite_count(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created')
    search_fields = ('user',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('slug', 'color', 'name')
