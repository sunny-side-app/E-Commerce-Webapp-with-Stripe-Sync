from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views

# from .views import CustomConfirmEmailView
from .views import (
    CustomConfirmEmailView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetView,
    RegisterUserView,
    SendConfirmationEmailView,
    UserListView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("clothes_shop.urls", namespace="clothes_shop")),
    path("api/auth/register/", RegisterUserView.as_view(), name="register"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path("api/auth/users/", UserListView.as_view(), name="user_list"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),  # token取得
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/auth/password/reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "api/auth/password/reset/confirm/<str:uidb64>/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "api/auth/registration/account-confirm-email/<str:uidb64>/<str:token>/",
        CustomConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),
    path(
        "api/auth/send-confirmation-email/",
        SendConfirmationEmailView.as_view(),
        name="send_confirmation_email",
    ),
]
