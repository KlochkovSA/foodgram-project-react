from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from recepts.models import Ingredient, Recipe, Tag

User = get_user_model()


class TestRecipe(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        Tag.objects.create(color='#FF0000', slug='breakfast', name='Затрак')
        Tag.objects.create(color='#00FF00', slug='dinner', name='Обед')
        Tag.objects.create(color='#00FF00', slug='supper', name='Ужин')
        Ingredient.objects.create(name='Картофель отварной',
                                  measurement_unit='г')
        Ingredient.objects.create(name='Капуста', measurement_unit='кг')

    def setUp(self):
        user = User.objects.create_user(username='test_user')
        self.authorized_client = APIClient()
        self.authorized_client.force_authenticate(user)
        self.guest = APIClient()

    def test_create_recipe(self):
        data = {
            "ingredients": [
                {
                    "id": 1,
                    "amount": 10
                }
            ],
            "tags": [
                1,
                2
            ],
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA"
                     "AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX"
                     "BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy"
                     "YQAAAABJRU5ErkJggg==",
            "name": "пирог",
            "text": "большой пирог",
            "cooking_time": 1
        }
        response = self.authorized_client.post('/api/recipes/', data=data,
                                               format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Recipe.objects.count(), 1)
        self.assertEqual(Recipe.objects.get().cooking_time, 1)

        response = self.client.get('/api/recipes/')
        self.assertContains(response, 'is_favorited')
        self.assertContains(response, 'is_in_shopping_cart')
