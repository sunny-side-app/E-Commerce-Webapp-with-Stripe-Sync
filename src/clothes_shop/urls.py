from django.urls import path

from . import views

app_name = "clothes_shop"

urlpatterns = [
    # Product API URLs
    path("api/products/", views.ProductListView.as_view(), name="product-list"),
    path("api/products/<int:pk>/", views.ProductDetailView.as_view(), name="product-detail"),
    # Order API URLs
    path("api/orders/", views.OrderListCreateView.as_view(), name="order-list-create"),
    path("api/orders/<int:pk>/", views.OrderDetailView.as_view(), name="order-detail"),
    # Review API URLs
    path(
        "api/product-reviews/<int:product_id>/",
        views.ProductReviewListView.as_view(),
        name="product-review-list",
    ),
    path(
        "api/product-reviews/<int:product_id>/user/<int:user_id>/",
        views.UserProductReviewDetailView.as_view(),
        name="user-product-review-detail",
    ),
    path(
        "api/user-reviews/<int:user_id>/",
        views.UserReviewListView.as_view(),
        name="user-review-list",
    ),
    # User API URLs
    path("api/users/", views.UserListCreateView.as_view(), name="user-list-create"),
    path("api/users/<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    # Favorite API URLs
    path("api/favorites/", views.FavoriteListCreateView.as_view(), name="favorite-list-create"),
    path("api/favorites/<int:pk>/", views.FavoriteDetailView.as_view(), name="favorite-detail"),
    # WishList API URLs
    path("api/wishlists/", views.WishListListCreateView.as_view(), name="wishlist-list-create"),
    path("api/wishlists/<int:pk>/", views.WishListDetailView.as_view(), name="wishlist-detail"),
    # CartItem API URLs
    path("api/cartitems/", views.CartItemListCreateView.as_view(), name="cartitem-list-create"),
    path("api/cartitems/<int:pk>/", views.CartItemDetailView.as_view(), name="cartitem-detail"),
    # OrderItem API URLs
    path("api/orderitems/", views.OrderItemListCreateView.as_view(), name="orderitem-list-create"),
    path("api/orderitems/<int:pk>/", views.OrderItemDetailView.as_view(), name="orderitem-detail"),
    # Payment API URLs
    path("api/payments/", views.PaymentListCreateView.as_view(), name="payment-list-create"),
    path("api/payments/<int:pk>/", views.PaymentDetailView.as_view(), name="payment-detail"),
    # Shipping API URLs
    path("api/shippings/", views.ShippingListCreateView.as_view(), name="shipping-list-create"),
    path("api/shippings/<int:pk>/", views.ShippingDetailView.as_view(), name="shipping-detail"),
    # Size API URLs
    path("api/sizes/", views.SizeListCreateView.as_view(), name="size-list-create"),
    path("api/sizes/<int:pk>/", views.SizeDetailView.as_view(), name="size-detail"),
    # Size API URLs
    path("api/sizes/", views.SizeListCreateView.as_view(), name="size-list-create"),
    path("api/sizes/<int:pk>/", views.SizeDetailView.as_view(), name="size-detail"),
    # Target API URLs
    path("api/targets/", views.TargetListCreateView.as_view(), name="target-list-create"),
    path("api/targets/<int:pk>/", views.TargetDetailView.as_view(), name="target-detail"),
    # ClothesType API URLs
    path(
        "api/clothestypes/",
        views.ClothesTypeListCreateView.as_view(),
        name="clothestype-list-create",
    ),
    path(
        "api/clothestypes/<int:pk>/",
        views.ClothesTypeDetailView.as_view(),
        name="clothestype-detail",
    ),
    # Brand API URLs
    path("api/brands/", views.BrandListCreateView.as_view(), name="brand-list-create"),
    path("api/brands/<int:pk>/", views.BrandDetailView.as_view(), name="brand-detail"),
    # ALL Categories
    path("api/categories/", views.CategoryListView.as_view(), name="category-list"),
]
