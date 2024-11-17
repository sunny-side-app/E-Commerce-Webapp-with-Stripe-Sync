from datetime import timedelta

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenObtainSerializer,
)
from rest_framework_simplejwt.tokens import AccessToken

from clothes_shop.models.user import User


class GuestAccessToken(AccessToken):
    lifetime = timedelta(minutes=5)


class GuestTokenObtainSerializer(TokenObtainSerializer):
    def get_token(cls, user):
        return GuestAccessToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)
        guest_user = User.objects.filter(role="guest").first()
        access_token = self.get_token(guest_user)
        data = {
            "access": str(access_token),
            "user": {
                "id": guest_user.id,
                "role": guest_user.role,
            },
        }
        return data


class LoginTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update(
            {
                "user": {
                    "id": self.user.id,
                    "name": self.user.name,
                    "email": self.user.email,
                    "role": self.user.role,
                }
            }
        )
        return data
