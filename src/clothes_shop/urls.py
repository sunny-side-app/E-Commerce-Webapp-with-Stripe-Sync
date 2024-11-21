from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from clothes_shop.views import (
    cart_views,
    category_views,
    check_access_views,
    checkout_views,
    favorite_views,
    order_views,
    payment_views,
    product_views,
    review_views,
    shipping_views,
    token_views,
    user_views,
    wishlist_views,
)

app_name = "clothes_shop"

urlpatterns = [
    path("api/token/", token_views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Product API URLs
    path("api/products/", product_views.ProductListView.as_view(), name="product-list"),
    path(
        "api/products/<int:pk>/",
        product_views.ProductDetailView.as_view(),
        name="product-detail",
    ),
    # Order API URLs
    path("api/orders/", order_views.OrderListCreateView.as_view(), name="order-list-create"),
    path("api/orders/<int:pk>/", order_views.OrderDetailView.as_view(), name="order-detail"),
    # Review API URLs
    path(
        "api/reviews/",
        review_views.ProductReviewListView.as_view(),
        name="product-review-list",
    ),
    path(
        "api/product-reviews/<int:product_id>/",
        review_views.UserProductReviewDetailView.as_view(),
        name="user-product-review-detail",
    ),
    # User API URLs
    path("api/users/", user_views.UserListCreateView.as_view(), name="user-list-create"),
    path("api/users/<int:user_id>/", user_views.UserDetailView.as_view(), name="user-detail"),
    path("api/profile/", user_views.UserProfileView.as_view(), name="user-profile"),
    path(
        "api/check-access/",
        check_access_views.CheckAccessAndAdminView.as_view(),
        name="check_access_and_admin",
    ),
    # Favorite API URLs
    path(
        "api/favorites/",
        favorite_views.FavoriteListCreateView.as_view(),
        name="favorite-list-create",
    ),
    path(
        "api/favorites/<int:pk>/",
        favorite_views.FavoriteDetailView.as_view(),
        name="favorite-detail",
    ),
    # WishList API URLs
    path(
        "api/wishlists/",
        wishlist_views.WishListListCreateView.as_view(),
        name="wishlist-list-create",
    ),
    path(
        "api/wishlists/<int:userId>/",
        wishlist_views.WishListDetailView.as_view(),
        name="wishlist-detail",
    ),
    # CartItem API URLs
    path(
        "api/cartitems/", cart_views.CartItemListCreateView.as_view(), name="cartitem-list-create"
    ),
    path(
        "api/cartitems/<int:pk>/", cart_views.CartItemDetailView.as_view(), name="cartitem-detail"
    ),
    # OrderItem API URLs
    path(
        "api/orderitems/",
        order_views.OrderItemListCreateView.as_view(),
        name="orderitem-list-create",
    ),
    path(
        "api/orderitems/<int:pk>/",
        order_views.OrderItemDetailView.as_view(),
        name="orderitem-detail",
    ),
    # Payment API URLs
    path(
        "api/payments/", payment_views.PaymentListCreateView.as_view(), name="payment-list-create"
    ),
    path(
        "api/payments/<int:pk>/", payment_views.PaymentDetailView.as_view(), name="payment-detail"
    ),
    # Shipping API URLs
    path(
        "api/shippings/",
        shipping_views.ShippingListCreateView.as_view(),
        name="shipping-list-create",
    ),
    path(
        "api/shippings/<int:pk>/",
        shipping_views.ShippingDetailView.as_view(),
        name="shipping-detail",
    ),
    # Size API URLs
    path("api/sizes/", category_views.SizeListCreateView.as_view(), name="size-list-create"),
    path("api/sizes/<int:pk>/", category_views.SizeDetailView.as_view(), name="size-detail"),
    # Size API URLs
    path("api/sizes/", category_views.SizeListCreateView.as_view(), name="size-list-create"),
    path("api/sizes/<int:pk>/", category_views.SizeDetailView.as_view(), name="size-detail"),
    # Target API URLs
    path("api/targets/", category_views.TargetListCreateView.as_view(), name="target-list-create"),
    path("api/targets/<int:pk>/", category_views.TargetDetailView.as_view(), name="target-detail"),
    # ClothesType API URLs
    path(
        "api/clothestypes/",
        category_views.ClothesTypeListCreateView.as_view(),
        name="clothestype-list-create",
    ),
    path(
        "api/clothestypes/<int:pk>/",
        category_views.ClothesTypeDetailView.as_view(),
        name="clothestype-detail",
    ),
    # Brand API URLs
    path("api/brands/", category_views.BrandListCreateView.as_view(), name="brand-list-create"),
    path("api/brands/<int:pk>/", category_views.BrandDetailView.as_view(), name="brand-detail"),
    # ALL Categories
    path("api/categories/", category_views.CategoryListView.as_view(), name="category-list"),
    # Stripe Checkout
    path("api/checkout/", checkout_views.StripeCheckoutView.as_view(), name="stripe-checkout"),
]
