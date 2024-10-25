from django.test import TestCase
from django.urls import resolve, reverse

from clothes_shop.views.product_views import ProductDetailView, ProductListView


class TestsUrls(TestCase):
    def test_list_url(self):
        url = reverse("clothes_shop:product-list")
        self.assertEqual(resolve(url).func.view_class, ProductListView)

    def test_detail_url(self):
        url = reverse("clothes_shop:product-detail", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func.view_class, ProductDetailView)
