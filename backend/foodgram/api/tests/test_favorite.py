from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from recepts.models import Recipe

User = get_user_model()


class TestFavorite(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')

        user = User.objects.create_user(username='test_user')
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user)

        cls.guest = APIClient()

    def test_favourite(self):
        recipe = Recipe.objects.create(name='Рецепт 1',
                                       text='Описание рецепта',
                                       author=self.author,
                                       cooking_time=1
                                       )
        url = f'/api/recipes/{recipe.pk}/favorite/'

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
