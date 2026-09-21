from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django.template.response import TemplateResponse
from django import forms
from .models import Product, Category, Cart, CartItem, Order, OrderItem, UserProfile, Review

class DeliveryTimeForm(forms.Form):
    delivery_date = forms.DateField(label='Ngày giao hàng', widget=forms.DateInput(attrs={'type': 'date'}))
    delivery_time = forms.TimeField(label='Giờ giao hàng', widget=forms.TimeInput(attrs={'type': 'time'}))

class OrderAdminForm(forms.ModelForm):
    delivery_date = forms.DateField(
        label='Ngày giao hàng',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    delivery_time = forms.TimeField(
        label='Giờ giao hàng',
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=False
    )

    class Meta:
        model = Order
        fields = '__all__'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'description', 'price', 'category', 'image')
        }),
        ('Trạng thái', {
            'fields': ('is_active',)
        }),
        ('Thông tin thêm', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')
    search_fields = ('product__name', 'cart__user__username')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ('id', 'user', 'full_name', 'total_amount', 'status', 'delivery_date', 'delivery_time', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'full_name', 'email')
    readonly_fields = ('created_at', 'updated_at', 'is_auto_delivered')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status__in=['shipping', 'delivered', 'review'])

    fieldsets = (
        ('Thông tin đơn hàng', {
            'fields': ('user', 'full_name', 'email', 'phone', 'address', 'payment_method', 'total_amount', 'status')
        }),
        ('Thông tin giao hàng', {
            'fields': ('delivery_date', 'delivery_time'),
            'description': 'Chọn ngày và giờ giao hàng'
        }),
        ('Thông tin thời gian', {
            'fields': ('created_at', 'updated_at', 'is_auto_delivered')
        }),
    )

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data:
            if obj.status == 'shipping':
                if not obj.delivery_date or not obj.delivery_time:
                    from django.core.exceptions import ValidationError
                    raise ValidationError('Vui lòng chọn ngày và giờ giao hàng khi chuyển trạng thái sang "Chờ giao hàng"')
                messages.success(request, f'Đơn hàng #{obj.id} đã được chuyển sang trạng thái "Chờ giao hàng" với thời gian giao hàng: {obj.delivery_date.strftime("%d/%m/%Y")} {obj.delivery_time.strftime("%H:%M")}')
            elif obj.status == 'delivered':
                messages.success(request, f'Đơn hàng #{obj.id} đã được chuyển sang trạng thái "Đã giao hàng"')
            elif obj.status == 'review':
                messages.success(request, f'Đơn hàng #{obj.id} đã được chuyển sang trạng thái "Đánh giá"')
        super().save_model(request, obj, form, change)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total_price', 'confirm_order_button')
    search_fields = ('order__id', 'product__name')
    list_filter = ('order__status',)
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(order__status='pending').order_by('-order__created_at')

    def confirm_order_button(self, obj):
        if obj.order.status == 'pending':
            return format_html(
                '<a class="button" href="{}">Xác nhận đơn hàng</a>',
                f'confirm-order/{obj.order.id}/'
            )
        return "-"
    confirm_order_button.short_description = 'Xác nhận đơn hàng'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'confirm-order/<int:order_id>/',
                self.admin_site.admin_view(self.confirm_order_view),
                name='orderitem-confirm-order',
            ),
        ]
        return custom_urls + urls

    def confirm_order_view(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            if request.method == 'POST':
                form = DeliveryTimeForm(request.POST)
                if form.is_valid():
                    delivery_date = form.cleaned_data['delivery_date']
                    delivery_time = form.cleaned_data['delivery_time']
                    
                    order.delivery_date = delivery_date
                    order.delivery_time = delivery_time
                    order.status = 'shipping'
                    order.save()
                    
                    messages.success(request, f'Đơn hàng #{order.id} đã được xác nhận và chuyển sang trạng thái "Chờ giao hàng" với thời gian giao hàng: {delivery_date.strftime("%d/%m/%Y")} {delivery_time.strftime("%H:%M")}')
                    return redirect('admin:accounts_orderitem_changelist')
            else:
                form = DeliveryTimeForm()
            
            context = {
                'title': 'Xác nhận đơn hàng',
                'order': order,
                'form': form,
                'opts': self.model._meta,
                'has_change_permission': self.has_change_permission(request, order),
            }
            return TemplateResponse(request, 'admin/order_confirm.html', context)
        except Order.DoesNotExist:
            messages.error(request, 'Không tìm thấy đơn hàng')
            return redirect('admin:accounts_orderitem_changelist')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'order', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'product__name', 'order__id')
