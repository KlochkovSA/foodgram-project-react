from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(
        max_length=50,
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
                                  related_name='recipes')
    ingredients = models.ManyToManyField(to='Ingredient', through='Amount',
                                         related_name='recipes')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']


class Amount(models.Model):
    ingredient_id = models.ForeignKey('Ingredient', related_name='amounts',
                                      on_delete=models.CASCADE)
    recipe_id = models.ForeignKey('Recipe', related_name='amounts',
                                  on_delete=models.CASCADE)
    amount = models.IntegerField(verbose_name='Количество')


class Tag(models.Model):
    slug = models.SlugField(unique=True)
    # length of hexadecimal color code is 6 + 1 (for # sign)
    # Example #FFFFFF -> White
    color = models.CharField(max_length=7)
    name = models.CharField(
        max_length=50,
        verbose_name='Тэг',
        unique=True
    )


class Ingredient(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название',
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единицы измерения',
    )

    def __str__(self):
        return self.name


class FavoriteRecipe(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,
                             related_name='favorite',
                             verbose_name='Пользователь',
                             on_delete=models.CASCADE
                             )
    recipe = models.ForeignKey(Recipe,
                               related_name='following',
                               verbose_name='Рецепт',
                               on_delete=models.CASCADE
                               )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'recipe']
        ordering = ['-created']


class ShoppingCart(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,
                             related_name='shopping_сart',
                             verbose_name='Подписчик',
                             on_delete=models.CASCADE
                             )
    recipe = models.ForeignKey(Recipe,
                               related_name='in_shopping_cart',
                               verbose_name='Рецепт',
                               on_delete=models.CASCADE
                               )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'recipe']
        ordering = ['-created']
