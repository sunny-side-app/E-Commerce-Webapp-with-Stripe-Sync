from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from clothes_shop.models.user import User

class UserAPITests(APITestCase):
    def test_user_creation(self):
        url = reverse("clothes_shop:user-list-create")
        data = {
            "email": "test@example.com",
            "password": "password",
            "name": "Test User",
            "role": "guest",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
