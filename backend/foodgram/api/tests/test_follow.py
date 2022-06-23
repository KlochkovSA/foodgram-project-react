from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from recepts.models import Recipe
from users.models import Follow

User = get_user_model()


class TestFollow(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user')
        self.author = User.objects.create_user(username='author')
        Recipe.objects.create(name='Рецепт 1',
                              text='Описание рецепта',
                              author=self.author,
                              cooking_time=1
                              )

        self.guest_client = APIClient()

        self.authorized_client = APIClient()
        self.authorized_client.force_authenticate(self.user)

    def test_subscribe(self):
        url = f'/api/users/{self.author.pk}/subscribe/'
        response = self.authorized_client.post(url)
        self.assertContains(response, 'Рецепт 1',
                            status_code=status.HTTP_201_CREATED)

    def test_unsubscribe(self):
        url = f'/api/users/{self.author.pk}/subscribe/'
        self.authorized_client.post(url)
        response = self.authorized_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_follow_list_response(self):
        Follow.objects.create(user=self.user, author=self.author)

        url = '/api/users/subscriptions/'
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.authorized_client.get(url)
        self.assertContains(response, 'Рецепт 1')
