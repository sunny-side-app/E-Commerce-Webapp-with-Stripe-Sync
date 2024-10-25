import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics

from clothes_shop.models import Shipping
from clothes_shop.serializers import ShippingSerializer

logger = logging.getLogger(__name__)


class ShippingListCreateView(generics.ListCreateAPIView):
    queryset = Shipping.objects.all()
    serializer_class = ShippingSerializer


class ShippingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shipping.objects.all()
    serializer_class = ShippingSerializer

    def get_object(self):
        return get_object_or_404(Shipping, pk=self.kwargs.get("pk"))
