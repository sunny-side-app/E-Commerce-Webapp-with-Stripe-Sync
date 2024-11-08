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

class UserProfileViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_user_profile(self):
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
