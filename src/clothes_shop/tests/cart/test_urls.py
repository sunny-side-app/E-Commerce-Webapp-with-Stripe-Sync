from django.test import TestCase
from django.urls import resolve, reverse

from clothes_shop.views import CartItemDetailView, CartItemListCreateView


class TestsUrls(TestCase):
    def test_list_url(self):
        url = reverse("clothes_shop:cartitem-list-create")
        self.assertEqual(resolve(url).func.view_class, CartItemListCreateView)

    def test_detail_url(self):
        url = reverse("clothes_shop:cartitem-detail", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func.view_class, CartItemDetailView)
