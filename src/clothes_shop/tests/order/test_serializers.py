from django.test import TestCase
from clothes_shop.models import Order, User
from clothes_shop.serializers import OrderSummarySerializer(, OrderWithItemsSerializer

class OrderSummarySerializer(Test(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(
            name="テストユーザー",
            email_address="testuser@example.com",
            role="customer",
            address="123 テストストリート"
        )
        self.order = Order.objects.create(
            user=self.user,
            order_status="pending",
            total_price=100.00
        )
        self.order_serializer = OrderSummarySerializer((self.order)
    
    def test_order_serializer_contains_expected_fields(self):
        self.assertEqual(
            set(self.order_serializer.data.keys()),
            {"id", "user", "order_date", "order_status", "total_price"}
        )
    
    def test_order_serializer_field_content(self):
        self.assertEqual(self.order_serializer.data["order_status"], self.order.order_status)


class OrderWithItemsSerializerTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(
            name="テストユーザー",
            email_address="testuser@example.com",
            role="customer",
            address="123 テストストリート"
        )
        self.order = Order.objects.create(
            user=self.user,
            order_status="pending",
            total_price=100.00
        )
        self.order_detail_serializer = OrderWithItemsSerializer(self.order)
    
    def test_order_detail_serializer_contains_expected_fields(self):
        self.assertEqual(
            set(self.order_detail_serializer.data.keys()),
            {"id", "user", "order_date", "order_status", "total_price", "order_items"}
        )
    
    def test_order_detail_serializer_field_content(self):
        self.assertEqual(self.order_detail_serializer.data["order_status"], self.order.order_status)
