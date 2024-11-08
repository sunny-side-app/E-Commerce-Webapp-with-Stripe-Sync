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
