from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from recipes.models import Recipe

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

        cls.recipe = Recipe.objects.create(name='Рецепт 1',
                                           text='Описание рецепта 1',
                                           author=cls.author,
                                           cooking_time=1
                                           )
        Recipe.objects.create(name='Рецепт 2',
                              text='Описание рецепта 2',
                              author=cls.author,
                              cooking_time=3
                              )

    def test_favourite(self):
        url = f'/api/recipes/{self.recipe.pk}/favorite/'

        response = self.guest.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.authorized_client.post(url)
        self.assertContains(response, 'cooking_time',
                            status_code=status.HTTP_201_CREATED)

        response = self.authorized_client.get('/api/recipes/?is_favorited=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        response = self.authorized_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.authorized_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.authorized_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
