from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from django.contrib import messages

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Tên loại')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Loại sản phẩm'
        verbose_name_plural = 'Loại sản phẩm'
        ordering = ['name']

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Tên sản phẩm')
    description = models.TextField(verbose_name='Mô tả')
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Giá')
    image = models.ImageField(upload_to='products/', verbose_name='Hình ảnh')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Loại sản phẩm')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')
    is_active = models.BooleanField(default=True, verbose_name='Kích hoạt')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Products'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart}"

class Order(models.Model):
    PAYMENT_METHODS = (
        ('cod', 'Cash on Delivery'),
        ('bank', 'Bank Transfer'),
    )

    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('shipping', 'Đang giao'),
        ('delivered', 'Đã giao'),
        ('review', 'Đã đánh giá')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_date = models.DateField(null=True, blank=True)
    delivery_time = models.TimeField(null=True, blank=True)
    is_auto_delivered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        
        # Tự động chuyển trạng thái khi đến thời gian giao hàng
        if self.delivery_date and self.delivery_time:
            delivery_datetime = timezone.make_aware(
                datetime.combine(self.delivery_date, self.delivery_time)
            )
            if timezone.now() >= delivery_datetime and not self.is_auto_delivered:
                self.status = 'delivered'
                self.is_auto_delivered = True
                messages.success(None, f'Đơn hàng #{self.id} đã được tự động chuyển sang trạng thái "Đã giao hàng"')
        
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Review(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.product:
            return f'Đánh giá sản phẩm {self.product.name} bởi {self.user.username}'
        return f'Đánh giá đơn hàng #{self.order.id} bởi {self.user.username}'
