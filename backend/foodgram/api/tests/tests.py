from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework import status

from recepts.models import Ingredient, Tag

TAG = {
    'name': 'Завтрак',
    'color': '#E26C2D',
    'slug': 'breakfast'
}

INGREDIENT = {
    'name': 'Капуста',
    'measurement_unit': 'кг'
}

User = get_user_model()


class TestIngredientURLs(TestCase):
    def setUp(self):
        measurement_unit = INGREDIENT['measurement_unit']
        Ingredient.objects.create(name=INGREDIENT['name'],
                                  measurement_unit=measurement_unit)
        self.guest_client = Client()

    def test_list(self):
        response = self.guest_client.get('/api/ingredients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        id = Ingredient.objects.first().id
        response = self.guest_client.get(f'/api/ingredients/{id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTagURLs(TestCase):
    def setUp(self):
        Tag.objects.create(name='Завтрак', color='#E26C2D', slug='breakfast')
        self.guest_client = Client()

    def test_list(self):
        response = self.guest_client.get('/api/tags/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        id = Tag.objects.first().id
        response = self.guest_client.get(f'/api/tags/{id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
