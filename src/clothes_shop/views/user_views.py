import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics

from clothes_shop.models.user import User
from clothes_shop.serializers.user_serializers import UserSerializer

logger = logging.getLogger(__name__)


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs.get("pk"))
