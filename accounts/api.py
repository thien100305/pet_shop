from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Avg, Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Order, OrderItem, OrderStatusHistory, Product, Review, UserProfile


User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "description", "product_count", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    image_url = serializers.URLField(source="image_link", required=False, allow_blank=True)

    class Meta:
        model = Product
        fields = (
            "id", "name", "description", "price", "image", "image_url", "category",
            "category_name", "is_active", "average_rating", "review_count", "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
        extra_kwargs = {"image": {"required": False}}

    def validate(self, attrs):
        if attrs.get("image") and attrs.get("image_link"):
            raise serializers.ValidationError("Chỉ chọn tệp ảnh hoặc URL ảnh.")
        if attrs.get("image_link"):
            attrs["image"] = None
        elif attrs.get("image"):
            attrs["image_link"] = ""
        return attrs


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_name", "quantity", "price", "subtotal")

    def get_subtotal(self, obj):
        return obj.price * obj.quantity


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    actor_name = serializers.CharField(source="actor.username", read_only=True, default=None)

    class Meta:
        model = OrderStatusHistory
        fields = ("id", "status", "status_label", "note", "actor", "actor_name", "created_at")


class OrderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    payment_label = serializers.CharField(source="get_payment_method_display", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    allowed_next_statuses = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id", "user", "username", "full_name", "email", "phone", "address",
            "payment_method", "payment_label", "total_amount", "status", "status_label",
            "tracking_number", "estimated_delivery_date", "delivery_date", "delivery_time",
            "allowed_next_statuses", "items", "status_history", "created_at", "updated_at",
        )
        read_only_fields = fields

    def get_allowed_next_statuses(self, obj):
        labels = dict(Order.STATUS_CHOICES)
        return [{"value": value, "label": labels[value]} for value in obj.allowed_next_statuses()]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("phone", "address", "city", "country", "postal_code")


class AdminUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    order_count = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(max_digits=14, decimal_places=0, read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "username", "first_name", "last_name", "email", "is_active", "is_staff",
            "date_joined", "last_login", "order_count", "total_spent", "profile",
        )
        read_only_fields = ("username", "is_staff", "date_joined", "last_login", "order_count", "total_spent", "profile")


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True, default=None)

    class Meta:
        model = Review
        fields = ("id", "order", "product", "product_name", "user", "username", "rating", "comment", "created_at", "updated_at")
        read_only_fields = fields


class AdminQueryMixin:
    permission_classes = (IsAdminUser,)

    def paginate_and_respond(self, queryset):
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        return self.get_paginated_response(serializer.data) if page is not None else Response(serializer.data)


class CategoryViewSet(AdminQueryMixin, viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset().annotate(product_count=Count("products"))
        query = self.request.query_params.get("q", "").strip()
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
        return queryset.order_by("name")


class ProductViewSet(AdminQueryMixin, viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def get_queryset(self):
        queryset = Product.objects.select_related("category").annotate(
            average_rating=Avg("reviews__rating"), review_count=Count("reviews", distinct=True)
        )
        query = self.request.query_params.get("q", "").strip()
        category = self.request.query_params.get("category")
        active = self.request.query_params.get("is_active")
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query))
        if category and category.isdigit():
            queryset = queryset.filter(category_id=category)
        if active in ("true", "false"):
            queryset = queryset.filter(is_active=active == "true")
        return queryset.order_by("-created_at")

    @action(detail=True, methods=("post",))
    def toggle_active(self, request, pk=None):
        product = self.get_object()
        product.is_active = not product.is_active
        product.save(update_fields=("is_active", "updated_at"))
        return Response(self.get_serializer(product).data)


class OrderViewSet(AdminQueryMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        queryset = Order.objects.select_related("user").prefetch_related("items__product", "status_history__actor")
        query = self.request.query_params.get("q", "").strip()
        order_status = self.request.query_params.get("status")
        payment_method = self.request.query_params.get("payment_method")
        if query:
            conditions = Q(full_name__icontains=query) | Q(phone__icontains=query) | Q(email__icontains=query) | Q(tracking_number__icontains=query)
            if query.lstrip("#").isdigit():
                conditions |= Q(id=int(query.lstrip("#")))
            queryset = queryset.filter(conditions)
        if order_status in dict(Order.STATUS_CHOICES):
            queryset = queryset.filter(status=order_status)
        if payment_method in dict(Order.PAYMENT_METHODS):
            queryset = queryset.filter(payment_method=payment_method)
        return queryset.order_by("-created_at")

    @action(detail=True, methods=("post",))
    def update_status(self, request, pk=None):
        order = self.get_object()
        next_status = request.data.get("status", "")
        if next_status not in order.allowed_next_statuses():
            return Response(
                {"detail": "Không thể chuyển sang trạng thái này.", "allowed": list(order.allowed_next_statuses())},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tracking_number = str(request.data.get("tracking_number", order.tracking_number)).strip()
        if next_status == "shipping" and not tracking_number:
            return Response({"detail": "Cần nhập mã vận đơn trước khi giao hàng."}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            order.status = next_status
            order.tracking_number = tracking_number
            order.estimated_delivery_date = request.data.get("estimated_delivery_date") or order.estimated_delivery_date
            order.save(update_fields=("status", "tracking_number", "estimated_delivery_date", "updated_at"))
            OrderStatusHistory.objects.create(
                order=order, status=next_status, actor=request.user,
                note=str(request.data.get("note", "")).strip() or f"Quản trị API cập nhật: {order.get_status_display()}.",
            )
        return Response(self.get_serializer(self.get_object()).data)


class CustomerViewSet(AdminQueryMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = AdminUserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        queryset = User.objects.filter(is_staff=False).select_related("profile").annotate(
            order_count=Count("orders", distinct=True),
            total_spent=Sum("orders__total_amount", filter=Q(orders__status__in=("delivered", "review"))),
        )
        query = self.request.query_params.get("q", "").strip()
        if query:
            queryset = queryset.filter(Q(username__icontains=query) | Q(email__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
        return queryset.order_by("-date_joined")

    @action(detail=True, methods=("post",))
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save(update_fields=("is_active",))
        return Response(self.get_serializer(user).data)


class ReviewViewSet(AdminQueryMixin, viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    http_method_names = ("get", "delete", "head", "options")

    def get_queryset(self):
        queryset = Review.objects.select_related("user", "product", "order")
        rating = self.request.query_params.get("rating")
        query = self.request.query_params.get("q", "").strip()
        if rating and rating.isdigit():
            queryset = queryset.filter(rating=int(rating))
        if query:
            queryset = queryset.filter(Q(comment__icontains=query) | Q(product__name__icontains=query) | Q(user__username__icontains=query))
        return queryset.order_by("-created_at")

class DashboardAPIView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        orders = Order.objects.all()
        completed = orders.filter(status__in=("delivered", "review"))
        start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        status_counts = {row["status"]: row["count"] for row in orders.values("status").annotate(count=Count("id"))}
        line_revenue = ExpressionWrapper(F("price") * F("quantity"), output_field=DecimalField(max_digits=14, decimal_places=0))
        top_products = OrderItem.objects.filter(order__status__in=("delivered", "review")).values(
            "product_id", "product__name"
        ).annotate(total_quantity=Sum("quantity"), revenue=Sum(line_revenue)).order_by("-total_quantity")[:10]
        return Response({
            "summary": {
                "products": Product.objects.count(),
                "active_products": Product.objects.filter(is_active=True).count(),
                "categories": Category.objects.count(),
                "customers": User.objects.filter(is_staff=False).count(),
                "orders": orders.count(),
                "pending_orders": status_counts.get("pending", 0),
                "reviews": Review.objects.count(),
                "average_rating": Review.objects.aggregate(value=Avg("rating"))["value"] or 0,
                "total_revenue": completed.aggregate(value=Sum("total_amount"))["value"] or 0,
                "monthly_revenue": completed.filter(created_at__gte=start_of_month).aggregate(value=Sum("total_amount"))["value"] or 0,
            },
            "orders_by_status": status_counts,
            "top_products": list(top_products),
            "recent_orders": OrderSerializer(
                orders.select_related("user").prefetch_related("items__product", "status_history__actor")[:10],
                many=True, context={"request": request},
            ).data,
        })
