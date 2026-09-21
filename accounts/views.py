from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Product, Category, Cart, CartItem, Order, OrderItem, UserProfile, Review
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Đăng nhập thành công!')
            return redirect('home')  # Chuyển hướng về trang chủ sau khi đăng nhập
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')
    
    return render(request, 'pages/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
            return render(request, 'pages/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại!')
            return render(request, 'pages/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã tồn tại!')
            return render(request, 'pages/register.html')
        
        # Tạo user mới
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
        return redirect('login')  # Chuyển hướng về trang đăng nhập
    
    return render(request, 'pages/register.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('home')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} has been added to your cart.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))  # Quay lại trang trước đó

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart')

@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    
    subtotal = sum(item.total_price for item in cart_items)
    total = subtotal  # No shipping fee for now
    
    # Get cart count for all views
    cart_count = CartItem.objects.filter(cart__user=request.user).count()
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'cart_count': cart_count
    })

@login_required
def checkout(request, product_id=None):
    if product_id:
        # Direct checkout for a single product
        product = get_object_or_404(Product, id=product_id)
        cart_items = [{'product': product, 'quantity': 1, 'total_price': product.price}]
        subtotal = product.price
    else:
        # Checkout from cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.cartitem_set.all()
        subtotal = sum(item.total_price for item in cart_items)
    
    total = subtotal  # No shipping fee for now
    
    # Get user profile information
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get cart count for all views
    cart_count = CartItem.objects.filter(cart__user=request.user).count()
    
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'cart_count': cart_count,
        'user_profile': user_profile  # Add user profile to context
    })

@login_required
def place_order(request):
    if request.method == 'POST':
        try:
            # Kiểm tra xem có phải đặt hàng trực tiếp không
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            
            if product_id:
                # Đặt hàng trực tiếp từ trang sản phẩm
                product = get_object_or_404(Product, id=product_id)
                total_amount = product.price * quantity
                
                # Tạo đơn hàng mới
                order = Order.objects.create(
                    user=request.user,
                    full_name=request.POST.get('full_name'),
                    email=request.POST.get('email'),
                    phone=request.POST.get('phone'),
                    address=request.POST.get('address'),
                    payment_method=request.POST.get('payment_method'),
                    total_amount=total_amount,
                    status='pending'
                )
                
                # Tạo chi tiết đơn hàng
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                
                messages.success(request, f'Đơn hàng #{order.id} đã được đặt thành công!')
                return redirect('order_confirmation', order_id=order.id)
                
            else:
                # Đặt hàng từ giỏ hàng
                cart = Cart.objects.get_or_create(user=request.user)[0]
                cart_items = cart.cartitem_set.all()
                
                if not cart_items:
                    messages.error(request, 'Giỏ hàng của bạn đang trống!')
                    return redirect('cart')
                
                # Tính tổng tiền từ giỏ hàng
                total_amount = sum(item.total_price for item in cart_items)
                
                # Tạo đơn hàng mới
                order = Order.objects.create(
                    user=request.user,
                    full_name=request.POST.get('full_name'),
                    email=request.POST.get('email'),
                    phone=request.POST.get('phone'),
                    address=request.POST.get('address'),
                    payment_method=request.POST.get('payment_method'),
                    total_amount=total_amount,
                    status='pending'
                )
                
                # Tạo chi tiết đơn hàng cho từng sản phẩm trong giỏ hàng
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )
                
                # Xóa giỏ hàng sau khi đặt hàng thành công
                cart_items.delete()
                
                messages.success(request, f'Đơn hàng #{order.id} đã được đặt thành công!')
                return redirect('order_confirmation', order_id=order.id)
            
        except Exception as e:
            # Nếu có lỗi, xóa đơn hàng nếu đã được tạo
            if 'order' in locals():
                order.delete()
            
            messages.error(request, f'Có lỗi xảy ra khi đặt hàng: {str(e)}')
            
            # Kiểm tra xem là đặt hàng trực tiếp hay từ giỏ hàng
            if product_id:
                return redirect('direct_order', product_id=product_id)
            else:
                return redirect('cart')
    
    # Nếu không phải POST request, kiểm tra có product_id không
    product_id = request.GET.get('product_id')
    if product_id:
        return redirect('direct_order', product_id=product_id)
    return redirect('cart')

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {
        'order': order,
        'cart_count': CartItem.objects.filter(cart__user=request.user).count()
    })

def search_products(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            is_active=True
        )
    else:
        products = Product.objects.filter(is_active=True)
    
    # Get cart count for all views
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(cart__user=request.user).count()
    
    return render(request, 'search_results.html', {
        'products': products,
        'query': query,
        'cart_count': cart_count
    })

@login_required
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    # Kiểm tra và cập nhật trạng thái đơn hàng
    for order in orders:
        if order.delivery_date and order.delivery_time:
            delivery_datetime = timezone.make_aware(
                datetime.combine(order.delivery_date, order.delivery_time)
            )
            if timezone.now() >= delivery_datetime and not order.is_auto_delivered:
                order.status = 'delivered'
                order.is_auto_delivered = True
                order.save()
                messages.success(request, f'Đơn hàng #{order.id} đã được tự động chuyển sang trạng thái "Đã giao hàng"')
    
    # Phân loại đơn hàng theo trạng thái
    pending_orders = orders.filter(status='pending')
    shipping_orders = orders.filter(status='shipping')
    delivered_orders = orders.filter(status='delivered')
    review_orders = orders.filter(status='review')
    
    # Lấy thông tin đánh giá cho mỗi đơn hàng
    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            item.review = Review.objects.filter(product=item.product, user=user).first()
    
    context = {
        'user': user,
        'orders': orders,
        'pending_orders': pending_orders,
        'shipping_orders': shipping_orders,
        'delivered_orders': delivered_orders,
        'review_orders': review_orders
    }
    return render(request, 'profile.html', context)

@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_profile.phone = request.POST.get('phone')
        user_profile.address = request.POST.get('address')
        user_profile.city = request.POST.get('city')
        user_profile.country = request.POST.get('country')
        user_profile.postal_code = request.POST.get('postal_code')
        user_profile.save()
        
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile')
    
    # Get cart count for all views
    cart_count = CartItem.objects.filter(cart__user=request.user).count()
    
    return render(request, 'edit_profile.html', {
        'user_profile': user_profile,
        'cart_count': cart_count
    })

@login_required
def confirm_received(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status == 'delivered':
        order.status = 'review'
        order.save()
        messages.success(request, 'Bạn đã xác nhận đã nhận đơn hàng. Vui lòng đánh giá đơn hàng.')
    else:
        messages.error(request, 'Không thể xác nhận đơn hàng này.')
    
    return redirect('profile')

@login_required
def review_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        for item in order.orderitem_set.all():
            rating = request.POST.get(f'rating_{item.id}')
            comment = request.POST.get(f'comment_{item.id}')
            
            if rating and comment:
                Review.objects.create(
                    order=order,
                    product=item.product,
                    user=request.user,
                    rating=rating,
                    comment=comment
                )
        
        messages.success(request, 'Cảm ơn bạn đã đánh giá đơn hàng!')
        return redirect('profile')
    
    return render(request, 'review_order.html', {
        'order': order,
        'cart_count': CartItem.objects.filter(cart__user=request.user).count()
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    review = Review.objects.filter(order=order).first()
    
    # Get cart count for all views
    cart_count = CartItem.objects.filter(cart__user=request.user).count()
    
    return render(request, 'order_detail.html', {
        'order': order,
        'order_items': order_items,
        'review': review,
        'cart_count': cart_count
    })

@login_required
def product_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    review = Review.objects.filter(product=product, user=request.user).first()
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            if review:
                # Update existing review
                review.rating = rating
                review.comment = comment
                review.save()
                messages.success(request, 'Đánh giá của bạn đã được cập nhật!')
            else:
                # Create new review
                Review.objects.create(
                    product=product,
                    user=request.user,
                    rating=rating,
                    comment=comment
                )
                messages.success(request, 'Cảm ơn bạn đã đánh giá sản phẩm!')
            return redirect('product_detail', product_id=product.id)
        else:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin đánh giá.')
    
    return render(request, 'product_review.html', {
        'product': product,
        'review': review,
        'cart_count': CartItem.objects.filter(cart__user=request.user).count()
    })

@login_required
def direct_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'product': product,
        'user': request.user,
        'cart_count': CartItem.objects.filter(cart__user=request.user).count()
    }
    return render(request, 'direct_order.html', context)
