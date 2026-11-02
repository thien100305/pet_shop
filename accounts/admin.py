from django.contrib import admin

from .models import Cart, CartItem, Category, Order, OrderItem, OrderStatusHistory, Product, Review, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name", "description")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category", "is_active", "created_at")
    list_filter = ("is_active", "category")
    list_editable = ("is_active",)
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ("status", "note", "actor", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "total_amount", "status", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("full_name", "phone", "email", "address")
    readonly_fields = ("user", "total_amount", "created_at", "updated_at")
    inlines = (OrderItemInline, OrderStatusHistoryInline)

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change:
            previous_status = Order.objects.filter(pk=obj.pk).values_list("status", flat=True).first()
        super().save_model(request, obj, form, change)
        if previous_status and previous_status != obj.status:
            OrderStatusHistory.objects.create(
                order=obj, status=obj.status, actor=request.user,
                note=f"Quản trị viên cập nhật: {obj.get_status_display()}.",
            )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__name", "user__username", "comment")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "city", "country")
    search_fields = ("user__username", "phone", "city")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "updated_at")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "total_price")


admin.site.site_header = "Quản trị PetHouse"
admin.site.site_title = "PetHouse Admin"
admin.site.index_title = "Quản lý cửa hàng"
