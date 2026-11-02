from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import CartItem, Category, Order, OrderStatusHistory, Product


class StoreFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="customer", email="customer@example.com", password="StrongPass123!")
        cls.staff = User.objects.create_user(username="manager", password="StrongPass123!", is_staff=True)
        category = Category.objects.create(name="Thú cưng kiểm thử")
        cls.product = Product.objects.create(
            name="Mèo Anh lông ngắn", description="Khỏe mạnh", price=5000000,
            category=category, image="products/1.jpg",
        )

    def test_home_and_product_pages(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        self.assertContains(self.client.get(reverse("product_detail", args=[self.product.id])), self.product.name)

    def test_cart_changes_require_login_and_post(self):
        url = reverse("add_to_cart", args=[self.product.id])
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertEqual(CartItem.objects.get(cart__user=self.user).quantity, 1)

    def test_checkout_creates_order_and_clears_cart(self):
        self.client.force_login(self.user)
        self.client.post(reverse("add_to_cart", args=[self.product.id]))
        response = self.client.post(reverse("place_order"), {
            "full_name": "Nguyễn Văn A", "email": "customer@example.com", "phone": "0900000000",
            "address": "Đà Nẵng", "payment_method": "cod", "quantity": 1,
        })
        order = Order.objects.get(user=self.user)
        self.assertRedirects(response, reverse("order_confirmation", args=[order.id]))
        self.assertEqual(order.total_amount, self.product.price)
        self.assertFalse(CartItem.objects.filter(cart__user=self.user).exists())
        self.assertTrue(OrderStatusHistory.objects.filter(order=order, status="pending").exists())

    def test_customer_can_track_order_and_confirm_delivery(self):
        order = Order.objects.create(
            user=self.user, full_name="Nguyễn Văn A", email=self.user.email,
            phone="0900000000", address="Đà Nẵng", payment_method="cod",
            total_amount=self.product.price, status="shipping", tracking_number="PET123456",
        )
        OrderStatusHistory.objects.create(order=order, status="shipping", note="Đơn đang trên đường giao.")
        self.client.force_login(self.user)
        detail = self.client.get(reverse("order_detail", args=[order.id]))
        self.assertContains(detail, "PET123456")
        self.assertContains(detail, "Đơn đang trên đường giao")
        response = self.client.post(reverse("confirm_received", args=[order.id]))
        self.assertRedirects(response, reverse("order_detail", args=[order.id]))
        order.refresh_from_db()
        self.assertEqual(order.status, "delivered")
        self.assertTrue(OrderStatusHistory.objects.filter(order=order, status="delivered").exists())

    def test_staff_must_follow_order_status_transitions(self):
        order = Order.objects.create(
            user=self.user, full_name="Nguyễn Văn A", email=self.user.email,
            phone="0900000000", address="Đà Nẵng", payment_method="cod",
            total_amount=self.product.price,
        )
        self.client.force_login(self.staff)
        url = reverse("admin_update_order", args=[order.id])
        self.client.post(url, {"status": "shipping", "tracking_number": "PET001"})
        order.refresh_from_db()
        self.assertEqual(order.status, "pending")
        self.client.post(url, {"status": "confirmed", "note": "Shop đã xác nhận."})
        order.refresh_from_db()
        self.assertEqual(order.status, "confirmed")
        self.assertTrue(OrderStatusHistory.objects.filter(order=order, status="confirmed").exists())

    def test_dashboard_is_staff_only(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("admin_dashboard")).status_code, 302)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse("admin_dashboard")).status_code, 200)
