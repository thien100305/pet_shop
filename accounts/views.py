from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.db.models import Avg, Count, Q, Sum
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import AdminCategoryForm, AdminProductForm, CheckoutForm, ProfileForm, RegisterForm
from .models import Cart, CartItem, Category, Order, OrderItem, OrderStatusHistory, Product, Review, UserProfile


staff_required = user_passes_test(lambda user: user.is_active and user.is_staff, login_url="login")


def home(request):
    selected_category = request.GET.get("category", "")
    products = Product.objects.filter(is_active=True).select_related("category").annotate(avg_rating=Avg("reviews__rating")).order_by("-created_at")
    if selected_category.isdigit():
        products = products.filter(category_id=int(selected_category))
    page_obj = Paginator(products, 8).get_page(request.GET.get("page"))
    return render(request, "home.html", {
        "products": page_obj,
        "categories": Category.objects.all(),
        "selected_category": selected_category,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related("category"), id=product_id, is_active=True)
    reviews = product.reviews.select_related("user")
    user_review = reviews.filter(user=request.user).first() if request.user.is_authenticated else None
    can_review = False
    if request.user.is_authenticated:
        can_review = OrderItem.objects.filter(
            order__user=request.user, order__status__in=["delivered", "review"], product=product
        ).exists()
    return render(request, "product_detail.html", {
        "product": product, "reviews": reviews, "user_review": user_review,
        "can_review": can_review, "average_rating": reviews.aggregate(value=Avg("rating"))["value"],
    })


def search_products(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.filter(is_active=True).select_related("category")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query))
    return render(request, "search_results.html", {"products": Paginator(products, 12).get_page(request.GET.get("page")), "query": query})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        user = authenticate(request, username=username, password=request.POST.get("password", ""))
        if user:
            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}, request.is_secure()):
                return redirect(next_url)
            return redirect("admin_dashboard" if user.is_staff else "home")
        messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
    return render(request, "pages/login.html", {"next": request.GET.get("next", "")})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Đăng ký thành công. Bạn có thể đăng nhập ngay.")
        return redirect("login")
    return render(request, "pages/register.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "Bạn đã đăng xuất.")
    return redirect("home")


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity = min(item.quantity + 1, 99)
        item.save(update_fields=["quantity", "updated_at"])
    messages.success(request, f"Đã thêm {product.name} vào giỏ hàng.")
    return redirect(request.POST.get("next") or "cart")


@login_required
def cart(request):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    items = cart_obj.items.select_related("product")
    subtotal = sum((item.total_price for item in items), Decimal("0"))
    return render(request, "cart.html", {"cart_items": items, "subtotal": subtotal, "total": subtotal})


@login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Số lượng không hợp lệ")
    if quantity <= 0:
        item.delete()
    else:
        item.quantity = min(quantity, 99)
        item.save(update_fields=["quantity", "updated_at"])
    return redirect("cart")


@login_required
@require_POST
def remove_from_cart(request, item_id):
    get_object_or_404(CartItem, id=item_id, cart__user=request.user).delete()
    messages.info(request, "Đã xóa sản phẩm khỏi giỏ hàng.")
    return redirect("cart")


def _checkout_items(user, product_id=None):
    if product_id:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        return [{"product": product, "quantity": 1, "total_price": product.price}]
    cart_obj, _ = Cart.objects.get_or_create(user=user)
    return list(cart_obj.items.select_related("product"))


@login_required
def checkout(request, product_id=None):
    items = _checkout_items(request.user, product_id)
    if not items:
        messages.warning(request, "Giỏ hàng đang trống.")
        return redirect("cart")
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    subtotal = sum((item["total_price"] if isinstance(item, dict) else item.total_price for item in items), Decimal("0"))
    initial = {
        "full_name": request.user.get_full_name() or request.user.username,
        "email": request.user.email, "phone": profile_obj.phone, "address": profile_obj.address,
        "payment_method": "cod", "product_id": product_id, "quantity": 1,
    }
    return render(request, "checkout.html", {"cart_items": items, "subtotal": subtotal, "total": subtotal, "form": CheckoutForm(initial=initial), "direct_product_id": product_id})


@login_required
@require_POST
def place_order(request):
    form = CheckoutForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Vui lòng kiểm tra lại thông tin nhận hàng.")
        product_id = request.POST.get("product_id")
        return redirect("checkout_product", product_id=product_id) if product_id else redirect("checkout_cart")

    data = form.cleaned_data
    product_id = data.get("product_id")
    with transaction.atomic():
        if product_id:
            product = get_object_or_404(Product.objects.select_for_update(), id=product_id, is_active=True)
            quantity = data.get("quantity") or 1
            rows = [(product, quantity)]
        else:
            cart_obj, _ = Cart.objects.get_or_create(user=request.user)
            cart_items = list(cart_obj.items.select_for_update().select_related("product"))
            if not cart_items:
                messages.warning(request, "Giỏ hàng đang trống.")
                return redirect("cart")
            rows = [(item.product, item.quantity) for item in cart_items]
        total = sum((product.price * quantity for product, quantity in rows), Decimal("0"))
        order = Order.objects.create(
            user=request.user, full_name=data["full_name"], email=data["email"], phone=data["phone"],
            address=data["address"], payment_method=data["payment_method"], total_amount=total,
        )
        OrderItem.objects.bulk_create([OrderItem(order=order, product=p, quantity=q, price=p.price) for p, q in rows])
        OrderStatusHistory.objects.create(
            order=order, status="pending", actor=request.user,
            note="Đơn hàng đã được đặt và đang chờ cửa hàng xác nhận.",
        )
        UserProfile.objects.update_or_create(user=request.user, defaults={"phone": data["phone"], "address": data["address"]})
        if not product_id:
            cart_obj.items.all().delete()
    messages.success(request, f"Đơn hàng #{order.id} đã được tạo thành công.")
    return redirect("order_confirmation", order_id=order.id)


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "order_confirmation.html", {"order": order})


@login_required
def profile(request):
    orders = list(Order.objects.filter(user=request.user).prefetch_related("items__product"))
    for order in orders:
        order.refresh_delivery_status()
    return render(request, "profile.html", {"orders": orders})


@login_required
def edit_profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile_obj, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Thông tin cá nhân đã được cập nhật.")
        return redirect("profile")
    return render(request, "edit_profile.html", {"form": form})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product", "reviews", "status_history"),
        id=order_id, user=request.user,
    )
    order.refresh_delivery_status()
    return render(request, "order_detail.html", {"order": order, "order_items": order.items.all()})


@login_required
@require_POST
def confirm_received(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status != "shipping":
        messages.error(request, "Đơn hàng này chưa ở trạng thái đang giao.")
    else:
        order.status = "delivered"
        order.is_auto_delivered = True
        order.save(update_fields=["status", "is_auto_delivered", "updated_at"])
        OrderStatusHistory.objects.create(
            order=order, status="delivered", actor=request.user,
            note="Khách hàng đã xác nhận nhận được hàng.",
        )
        messages.success(request, "Đã xác nhận nhận hàng. Cảm ơn bạn!")
    return redirect("order_detail", order_id=order.id)


@login_required
def review_order(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), id=order_id, user=request.user, status__in=["delivered", "review"])
    if request.method == "POST":
        saved = 0
        for item in order.items.all():
            rating = request.POST.get(f"rating_{item.id}")
            comment = request.POST.get(f"comment_{item.id}", "").strip()
            if rating and comment and rating.isdigit() and 1 <= int(rating) <= 5:
                Review.objects.update_or_create(user=request.user, product=item.product, defaults={"order": order, "rating": int(rating), "comment": comment})
                saved += 1
        if saved:
            order.status = "review"
            order.save(update_fields=["status", "updated_at"])
            OrderStatusHistory.objects.create(
                order=order, status="review", actor=request.user,
                note="Khách hàng đã đánh giá sản phẩm.",
            )
            messages.success(request, "Cảm ơn bạn đã đánh giá sản phẩm.")
            return redirect("order_detail", order_id=order.id)
        messages.error(request, "Vui lòng chọn số sao và nhập nhận xét.")
    return render(request, "review_order.html", {"order": order})


@login_required
def product_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    purchased = OrderItem.objects.filter(order__user=request.user, order__status__in=["delivered", "review"], product=product).order_by("-order__created_at").first()
    if not purchased:
        messages.error(request, "Bạn chỉ có thể đánh giá sản phẩm đã mua và nhận hàng.")
        return redirect("product_detail", product_id=product.id)
    review = Review.objects.filter(product=product, user=request.user).first()
    if request.method == "POST":
        rating = request.POST.get("rating", "")
        comment = request.POST.get("comment", "").strip()
        if rating.isdigit() and 1 <= int(rating) <= 5 and comment:
            Review.objects.update_or_create(user=request.user, product=product, defaults={"order": purchased.order, "rating": int(rating), "comment": comment})
            messages.success(request, "Đánh giá của bạn đã được lưu.")
            return redirect("product_detail", product_id=product.id)
        messages.error(request, "Vui lòng chọn từ 1 đến 5 sao và nhập nhận xét.")
    return render(request, "product_review.html", {"product": product, "review": review})


@staff_required
def admin_dashboard(request):
    orders = Order.objects.select_related("user").order_by("-created_at")
    revenue = orders.filter(status__in=["delivered", "review"]).aggregate(total=Sum("total_amount"))["total"] or 0
    recent_orders = list(orders[:12])
    status_labels = dict(Order.STATUS_CHOICES)
    for order in recent_orders:
        order.allowed_status_choices = [
            (value, status_labels[value]) for value in order.allowed_next_statuses()
        ]
    return render(request, "admin_dashboard.html", {
        "product_count": Product.objects.count(), "customer_count": Order.objects.values("user_id").distinct().count(),
        "pending_count": orders.filter(status="pending").count(), "revenue": revenue,
        "recent_orders": recent_orders,
        "category_count": Category.objects.count(),
    })


@staff_required
def admin_products(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.select_related("category").order_by("-created_at")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(category__name__icontains=query))
    return render(request, "admin/products.html", {"products": products, "query": query})


@staff_required
def admin_product_create(request):
    form = AdminProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"Đã thêm sản phẩm {product.name}.")
        return redirect("admin_products")
    return render(request, "admin/product_form.html", {"form": form, "page_title": "Thêm sản phẩm"})


@staff_required
def admin_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = AdminProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Đã cập nhật sản phẩm {product.name}.")
        return redirect("admin_products")
    return render(request, "admin/product_form.html", {"form": form, "page_title": "Sửa sản phẩm", "product": product})


@staff_required
@require_POST
def admin_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        name = product.name
        product.delete()
        messages.success(request, f"Đã xóa sản phẩm {name}.")
    except ProtectedError:
        messages.error(request, "Không thể xóa sản phẩm đã xuất hiện trong đơn hàng. Hãy tắt trạng thái đang bán.")
    return redirect("admin_products")


@staff_required
def admin_categories(request):
    categories = Category.objects.annotate(product_count=Count("products")).order_by("name")
    return render(request, "admin/categories.html", {"categories": categories})


@staff_required
def admin_category_create(request):
    form = AdminCategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(request, f"Đã thêm danh mục {category.name}.")
        return redirect("admin_categories")
    return render(request, "admin/category_form.html", {"form": form, "page_title": "Thêm danh mục"})


@staff_required
def admin_category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    form = AdminCategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Đã cập nhật danh mục {category.name}.")
        return redirect("admin_categories")
    return render(request, "admin/category_form.html", {"form": form, "page_title": "Sửa danh mục", "category": category})


@staff_required
@require_POST
def admin_category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    try:
        name = category.name
        category.delete()
        messages.success(request, f"Đã xóa danh mục {name}.")
    except ProtectedError:
        messages.error(request, "Không thể xóa danh mục đang có sản phẩm.")
    return redirect("admin_categories")


@staff_required
@require_POST
def admin_update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    statuses = dict(Order.STATUS_CHOICES)
    status = request.POST.get("status")
    if status not in statuses:
        return HttpResponseBadRequest("Trạng thái không hợp lệ")
    if status not in order.allowed_next_statuses():
        messages.error(request, "Không thể chuyển sang trạng thái này từ trạng thái hiện tại.")
        return redirect(reverse("admin_dashboard"))
    tracking_number = request.POST.get("tracking_number", "").strip()
    estimated_delivery_date = request.POST.get("estimated_delivery_date") or None
    if status == "shipping" and not tracking_number:
        messages.error(request, "Vui lòng nhập mã vận đơn trước khi chuyển sang đang giao.")
        return redirect(reverse("admin_dashboard"))
    with transaction.atomic():
        order.status = status
        update_fields = ["status", "updated_at"]
        if tracking_number:
            order.tracking_number = tracking_number
            update_fields.append("tracking_number")
        if estimated_delivery_date:
            order.estimated_delivery_date = estimated_delivery_date
            update_fields.append("estimated_delivery_date")
        order.save(update_fields=update_fields)
        OrderStatusHistory.objects.create(
            order=order, status=status, actor=request.user,
            note=request.POST.get("note", "").strip() or f"Cửa hàng cập nhật: {statuses[status]}.",
        )
    messages.success(request, f"Đã cập nhật đơn hàng #{order.id}: {statuses[status]}.")
    return redirect(reverse("admin_dashboard"))
