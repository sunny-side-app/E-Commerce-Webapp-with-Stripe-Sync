import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics

from clothes_shop.models.user_interaction import WishList
from clothes_shop.serializers.user_interaction_serializers import WishListSerializer

logger = logging.getLogger(__name__)


class WishListListCreateView(generics.ListCreateAPIView):
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer


class WishListDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer

    def get_object(self):
        return get_object_or_404(WishList, pk=self.kwargs.get("pk"))
