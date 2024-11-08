from clothes_shop.models.user import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class UserAPITests(APITestCase):
    def test_CRUD_user(self):
        user_list_create_url = reverse("clothes_shop:user-list-create")
        initial_user_data = {
            "stripe_customer_id": "hogehoge",
            "email": "test@example.com",
            "password": "password",
            "name": "Test User",
            "role": "guest",
        }
        response_post = self.client.post(user_list_create_url, initial_user_data, format="json")
        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)

        user_detail_url = reverse(
            "clothes_shop:user-detail", kwargs={"user_id": response_post.data["id"]}
        )
        response_get = self.client.get(user_detail_url)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_get.data["name"], initial_user_data["name"])

        updated_user_data = {
            "email": "test_updated@example.com",
            "password": "password_updated",
            "name": "Super Test User",
        }
        response_put = self.client.put(user_detail_url, updated_user_data, format="json")
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_put.data["name"], updated_user_data["name"])

        delete_user_data = {"id": response_get.data["id"]}
        response_delete = self.client.delete(user_detail_url, delete_user_data, format="json")
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)

class UserProfileViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            name="Test User",
            password="testpass",
            role="registered"
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile(self):
        url = reverse('clothes_shop:user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.user.name)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['role'], self.user.role)
        self.assertEqual(response.data['address'], self.user.address)
        self.assertEqual(response.data['is_active'], self.user.is_active)

    def test_update_user_profile(self):
        url = reverse('clothes_shop:user-profile') 
        data = {'name': 'Updated User', 'address': '123 Updated Street'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Updated User')
        self.assertEqual(self.user.address, '123 Updated Street')

    def test_delete_user_profile(self):
        url = reverse('clothes_shop:user-profile') 
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(email="testuser@example.com").exists())
