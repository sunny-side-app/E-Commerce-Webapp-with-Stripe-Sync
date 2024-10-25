import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics

from clothes_shop.models import Order, OrderItem
from clothes_shop.serializers import OrderItemSerializer, OrderSerializer

logger = logging.getLogger(__name__)


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_object(self):
        return get_object_or_404(Order, pk=self.kwargs.get("pk"))


class OrderItemListCreateView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class OrderItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def get_object(self):
        return get_object_or_404(OrderItem, pk=self.kwargs.get("pk"))
