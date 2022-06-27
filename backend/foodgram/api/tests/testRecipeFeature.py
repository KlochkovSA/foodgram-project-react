import json

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
        cls.tag1 = Tag.objects.create(color='#FF0000', slug='breakfast',
                                      name='Затрак')
        cls.tag2 = Tag.objects.create(color='#00FF00', slug='dinner',
                                      name='Обед')
        cls.tag3 = Tag.objects.create(color='#00FF00', slug='supper',
                                      name='Ужин')
        Ingredient.objects.create(name='Картофель отварной',
                                  measurement_unit='г')
        Ingredient.objects.create(name='Капуста', measurement_unit='кг')

    def setUp(self):
        user = User.objects.create_user(username='test_user')
        self.authorized_client = APIClient()
        self.authorized_client.force_authenticate(user)
        self.guest = APIClient()

    def test_recipe(self):
        data = {
            "ingredients": [
                {
                    "id": 1,
                    "amount": 10
                }
            ],
            "tags": [
                1
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
        recipe = Recipe.objects.get()
        self.assertEqual(recipe.cooking_time, 1)

        response = self.client.get('/api/recipes/')
        self.assertContains(response, 'is_favorited')
        self.assertContains(response, 'is_in_shopping_cart')

        recipe = Recipe.objects.create(name='Рецепт 1', text='Описание',
                                       cooking_time=10,
                                       author=self.author)
        recipe.tags.add(self.tag3)

        response = self.authorized_client.get(
            f'/api/recipes/?tags={self.tag3.slug}')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.authorized_client.get(
            f'/api/recipes/?tags={self.tag1.slug}&tags={self.tag3.slug}')
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.authorized_client.get(
            f'/api/recipes/?author={self.author.pk}&tags={self.tag2.slug}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

        data = {
            "ingredients": [
                {
                    "id": 2,
                    "amount": 1
                }
            ],
            "tags": [
                3
            ],
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA"
                     "AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX"
                     "BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy"
                     "YQAAAABJRU5ErkJggg==",
            "name": "пирог",
            "text": "большой пирог",
            "cooking_time": 1
        }
        response = self.authorized_client.patch(
            f'/api/recipes/{recipe.pk}/edit/',
            data=data,
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверка ответа
        self.assertEqual(3, response.data['tags'][0]['id'])
        self.assertEqual(1, response.data['tags'].__len__())
        self.assertEqual(2, response.data['ingredients'][0]['id'])
        self.assertEqual(1, response.data['ingredients'][0]['amount'])
        self.assertEqual(1, response.data['ingredients'].__len__())

        # Проверка ответа при новом запросе
        response = self.authorized_client.get(f'/api/recipes/{recipe.pk}/')
        self.assertEqual(3, response.data['tags'][0]['id'])
        self.assertEqual(1, response.data['tags'].__len__())
        self.assertEqual(2, response.data['ingredients'][0]['id'])
        self.assertEqual(1, response.data['ingredients'][0]['amount'])
        self.assertEqual(1, response.data['ingredients'].__len__())

