from django.test import TestCase
from django.utils import timezone
from clothes_shop.models import Order, User, Product, OrderItem, Size, Target, ClothesType, Brand
from clothes_shop.serializers import OrderSummarySerializer, OrderWithItemsSerializer

class OrderSummarySerializerTest(TestCase):
    
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
        self.order_serializer = OrderSummarySerializer(self.order)
    
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
        self.size = Size.objects.create(
            name="M"
        )
        self.target = Target.objects.create(
            name="Men"
        )
        self.clothes_type = ClothesType.objects.create(
            name="シャツ"
        )
        self.brand = Brand.objects.create(
            name="テストブランド"
        )

        self.product = Product.objects.create(
            name="テスト商品",
            description="テスト商品説明",
            price=50.00,
            stock_quantity=10,
            size=self.size,
            target=self.target,
            clothes_type=self.clothes_type,
            brand=self.brand,
            release_date=timezone.now()
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            unit_price=self.product.price
        )
        self.order_detail_serializer = OrderWithItemsSerializer(self.order)

    
    def test_order_detail_serializer_contains_expected_fields(self):
        self.assertEqual(
            set(self.order_detail_serializer.data.keys()),
            {"id", "user", "order_date", "order_status", "total_price", "order_items"}
        )
    
    def test_order_detail_serializer_field_content(self):
        self.assertEqual(self.order_detail_serializer.data["order_status"], self.order.order_status)

    def test_order_items_include_product_details(self):
        order_items = self.order_detail_serializer.data["order_items"]
        self.assertEqual(len(order_items), 1)
        
        order_item_data = order_items[0]
        self.assertEqual(order_item_data["product"]["id"], self.product.id)
        self.assertEqual(order_item_data["product"]["name"], self.product.name)
        self.assertEqual(order_item_data["quantity"], self.order_item.quantity)
        self.assertEqual(order_item_data["unit_price"], self.order_item.unit_price)

