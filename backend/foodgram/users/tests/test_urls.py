from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from rest_framework import status

User = get_user_model()

USER1_DATA = {
    'email': 'vpupkin@yandex.ru',
    'username': 'vasya.pupkin',
    'first_name': 'Вася',
    'last_name': 'Пупкин',
    'password': 'Qwerty123',
    'id': 0,
}


def create_fixtures():
    user = User.objects.create_user(username=USER1_DATA['username'],
                                    email=USER1_DATA['email'],
                                    first_name=USER1_DATA['first_name'],
                                    last_name=USER1_DATA['last_name'],
                                    password=USER1_DATA['password'])
    fixtures = {
        'user1': user,
    }
    return fixtures


class TestTokenURL(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.fixtures = create_fixtures()
        self.authorized_client.force_login(user=self.fixtures['user1'])

    def testGetToken(self):
        data = {
            'password': USER1_DATA['password'],
            'email': USER1_DATA['email']
        }
        response = self.guest_client.post('/api/auth/token/login/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testDeleteToken(self):
        data = {
            'password': USER1_DATA['password'],
            'email': USER1_DATA['email']
        }
        response = self.guest_client.post('/api/auth/token/login/', data=data)
        token = response.data['auth_token']
        response = self.guest_client.post('/api/auth/token/logout/', HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TestUsersFeature(TestCase):
    def setUp(self):
        self.guest_client = Client()
        authorized_client = Client()
        self.fixtures = create_fixtures()
        data = {
            'password': USER1_DATA['password'],
            'email': USER1_DATA['email']
        }
        response = authorized_client.post('/api/auth/token/login/', data=data)
        token = response.data['auth_token']

        self.authorized_client = Client(HTTP_AUTHORIZATION=f'Token {token}')

    def testGetUsers(self):
        response = self.guest_client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testGetPersonalProfile(self):
        response = self.guest_client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.authorized_client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testGetProfile(self):
        id = self.fixtures['user1'].id
        profile_url = f'/api/users/{id}/'
        response = self.guest_client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.authorized_client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testChangePassword(self):
        url = '/api/users/set_password/'
        data = {'new_password': '12dfssdfdsfdsds3',
                'current_password': USER1_DATA['password']}

        response = self.guest_client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.authorized_client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
