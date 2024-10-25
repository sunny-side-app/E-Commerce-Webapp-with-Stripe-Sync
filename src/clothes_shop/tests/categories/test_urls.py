from django.test import TestCase
from django.urls import resolve, reverse

from clothes_shop.views.category_views import (
    BrandDetailView,
    BrandListCreateView,
    CategoryListView,
    ClothesTypeDetailView,
    ClothesTypeListCreateView,
    SizeDetailView,
    SizeListCreateView,
    TargetDetailView,
    TargetListCreateView,
)


class TestsUrls(TestCase):

    # 全カテゴリ取得API
    def test_category_list_url(self):
        # "api/categories/"で期待したビューにとぶか確認
        url = reverse("clothes_shop:category-list")
        self.assertEqual(resolve(url).func.view_class, CategoryListView)

    # Size API URLs
    def test_size_list_url(self):
        url = reverse("clothes_shop:size-list-create")
        self.assertEqual(resolve(url).func.view_class, SizeListCreateView)

    def test_size_detail_url(self):
        url = reverse("clothes_shop:size-detail", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func.view_class, SizeDetailView)

    # Target API URLs
    def test_target_list_url(self):
        url = reverse("clothes_shop:target-list-create")
        self.assertEqual(resolve(url).func.view_class, TargetListCreateView)

    def test_target_detail_url(self):
        url = reverse("clothes_shop:target-detail", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func.view_class, TargetDetailView)

    # ClothesType API URLs
    def test_clothes_type_list_url(self):
        url = reverse("clothes_shop:clothestype-list-create")
        self.assertEqual(resolve(url).func.view_class, ClothesTypeListCreateView)

    def test_clothes_type_detail_url(self):
        url = reverse("clothes_shop:clothestype-detail", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func.view_class, ClothesTypeDetailView)

    # Brand API URLs
    def test_brand_list_url(self):
        url = reverse("clothes_shop:brand-list-create")
        self.assertEqual(resolve(url).func.view_class, BrandListCreateView)

    def test_brand_detail_url(self):
        url = reverse("clothes_shop:brand-detail", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func.view_class, BrandDetailView)
