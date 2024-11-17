import logging

from rest_framework_simplejwt.views import TokenObtainPairView, TokenViewBase

from clothes_shop.serializers.token_serializers import (
    GuestTokenObtainSerializer,
    LoginTokenObtainPairSerializer,
)

logger = logging.getLogger(__name__)


class GuestTokenObtainPairView(TokenViewBase):
    serializer_class = GuestTokenObtainSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = LoginTokenObtainPairSerializer
