from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.users.models import User

User = get_user_model()

# Test cases for user authentication (login and registration)
class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com",
            password="test@123"
        )
        self.login_url = reverse('login')
        self.register_url = reverse('register')

    def test_sucessful_login(self):
        """Testing Successful Login"""
        data = {
            "email": "test@gmail.com",
            "password": "test@123"
        }
        response = self.client.post(self.login_url, data)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_unsucessful_login(self):
        """Testing Unsuccessful Login"""
        data = {
            "email": "test@gmail.com",
            "password": "wrongpassword" 
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_registration(self):
        """Testing Successful Registration"""
        data = {
            "email": "new_test@gmail.com",
            "password": "newTest@123"
        }
        response = self.client.post(self.register_url, data)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response_data)
        self.assertEqual(response_data['email'], data['email'])
