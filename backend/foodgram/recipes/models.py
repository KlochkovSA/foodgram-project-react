from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Имя'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        help_text='Загрузить фото',
        upload_to='recipes/images/',
        blank=False
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах'
    )
    author = models.ForeignKey(User,
                               related_name='recipes',
                               verbose_name='Автор',
                               on_delete=models.CASCADE
                               )
    tags = models.ManyToManyField(to='Tag', db_table='RecipeTag',
                                  verbose_name='Тэги',
                                  related_name='recipes')
    ingredients = models.ManyToManyField(to='Ingredient', through='Amount',
                                         verbose_name='Ингредиенты',
                                         related_name='recipes')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        models.UniqueConstraint(
            fields=['author', 'name'],
            name='unique_recipe_name'
        )
        ordering = ['-created']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Amount(models.Model):
    ingredient_id = models.ForeignKey('Ingredient', related_name='amounts',
                                      on_delete=models.CASCADE)
    recipe_id = models.ForeignKey('Recipe', related_name='amounts',
                                  on_delete=models.CASCADE)
    amount = models.IntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Количество'
        verbose_name_plural = 'Количества ингредиентов'


class Tag(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    # length of hexadecimal color code is 6 + 1 (for # sign)
    # Example #FFFFFF -> White
    color = models.CharField(max_length=7)
    name = models.CharField(
        max_length=200,
        verbose_name='Тэг',
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единицы измерения',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class FavoriteRecipe(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,
                             related_name='favorite_recipes',
                             verbose_name='Пользователь',
                             on_delete=models.CASCADE
                             )
    recipe = models.ForeignKey(Recipe,
                               related_name='in_favorite',
                               verbose_name='Рецепт',
                               on_delete=models.CASCADE
                               )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe'
            )
        ]
        ordering = ['-created']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,
                             related_name='shopping_сart',
                             verbose_name='Покупатель',
                             on_delete=models.CASCADE
                             )
    recipe = models.ForeignKey(Recipe,
                               related_name='in_shopping_cart',
                               verbose_name='Рецепт',
                               on_delete=models.CASCADE
                               )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_cart'
            )
        ]
        ordering = ['-created']
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
