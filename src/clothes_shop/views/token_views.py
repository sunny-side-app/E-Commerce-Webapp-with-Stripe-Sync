import logging

from rest_framework_simplejwt.views import TokenObtainPairView

from clothes_shop.serializers.token_serializers import CustomTokenObtainPairSerializer

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
