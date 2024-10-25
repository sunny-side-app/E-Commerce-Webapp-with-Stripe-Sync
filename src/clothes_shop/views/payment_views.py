import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics

from clothes_shop.models import Payment
from clothes_shop.serializers import PaymentSerializer

logger = logging.getLogger(__name__)


class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_object(self):
        return get_object_or_404(Payment, pk=self.kwargs.get("pk"))
