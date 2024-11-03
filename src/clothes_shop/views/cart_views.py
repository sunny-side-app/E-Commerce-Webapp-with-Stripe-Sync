import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics

from clothes_shop.models import CartItem
from clothes_shop.serializers import CartItemSerializer

logger = logging.getLogger(__name__)


class CartItemListCreateView(generics.ListCreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_object(self):
        return get_object_or_404(CartItem, pk=self.kwargs.get("pk"))
