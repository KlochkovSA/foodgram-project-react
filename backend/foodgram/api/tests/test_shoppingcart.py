from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from recepts.models import Amount, Ingredient, Recipe

User = get_user_model()


class TestShoppingCart(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')

        user = User.objects.create_user(username='test_user')
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user)

        cls.guest = APIClient()

        ingredient_1 = Ingredient.objects.create(name='Картофель отварной',
                                                 measurement_unit='г')
        ingredient_2 = Ingredient.objects.create(name='Капуста',
                                                 measurement_unit='кг')

        cls.recipe = Recipe.objects.create(name='Рецепт 1',
                                           text='Описание рецепта',
                                           author=cls.author,
                                           cooking_time=1,
                                           )
        Amount.objects.create(ingredient_id=ingredient_1, recipe_id=cls.recipe,
                              amount=5)
        Amount.objects.create(ingredient_id=ingredient_2, recipe_id=cls.recipe,
                              amount=15)

    def test_shopping_cart(self):
        url = f'/api/recipes/{self.recipe.pk}/shopping_cart/'

        response = self.guest.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.authorized_client.post(url)
        self.assertContains(response, 'cooking_time',
                            status_code=status.HTTP_201_CREATED)

        response = self.authorized_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.authorized_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.authorized_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_download_shopping_cart(self):
        url = '/api/recipes/download_shopping_cart/'
        response = self.guest.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authorized_client.post(
            f'/api/recipes/{self.recipe.pk}/shopping_cart/')

        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
