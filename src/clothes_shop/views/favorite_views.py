import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics

from clothes_shop.models.user_interaction import Favorite
from clothes_shop.serializers import FavoriteSerializer

logger = logging.getLogger(__name__)


class FavoriteListCreateView(generics.ListCreateAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class FavoriteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def get_object(self):
        return get_object_or_404(Favorite, pk=self.kwargs.get("pk"))
