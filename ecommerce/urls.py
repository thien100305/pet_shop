"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from accounts.models import Product, Category, Review
from django.shortcuts import render, get_object_or_404
from accounts import views
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def home_view(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    page = request.GET.get('page', 1)
    
    if selected_category:
        products = Product.objects.filter(category_id=selected_category, is_active=True)
    else:
        products = Product.objects.filter(is_active=True)
    
    # Phân trang
    paginator = Paginator(products, 5)  # Luôn hiển thị 5 sản phẩm mỗi trang
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    # Get cart count for all views
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = views.CartItem.objects.filter(cart__user=request.user).count()
        
    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'cart_count': cart_count
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Get user's review if exists
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()
    
    # Get cart count for all views
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = views.CartItem.objects.filter(cart__user=request.user).count()
    
    return render(request, 'product_detail.html', {
        'product': product,
        'user_review': user_review,
        'cart_count': cart_count
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('search/', views.search_products, name='search'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', login_required(views.add_to_cart), name='add_to_cart'),
    path('cart/', login_required(views.cart), name='cart'),
    path('update-cart/<int:item_id>/', login_required(views.update_cart), name='update_cart'),
    path('remove-from-cart/<int:item_id>/', login_required(views.remove_from_cart), name='remove_from_cart'),
    path('checkout/product/<int:product_id>/', login_required(views.checkout), name='checkout_product'),
    path('checkout/cart/', login_required(views.checkout), name='checkout_cart'),
    path('place-order/', login_required(views.place_order), name='place_order'),
    path('order-confirmation/<int:order_id>/', login_required(views.order_confirmation), name='order_confirmation'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', login_required(views.profile), name='profile'),
    path('profile/edit/', login_required(views.edit_profile), name='edit_profile'),
    path('order/<int:order_id>/', login_required(views.order_detail), name='order_detail'),
    path('confirm-received/<int:order_id>/', login_required(views.confirm_received), name='confirm_received'),
    path('review-order/<int:order_id>/', login_required(views.review_order), name='review_order'),
    path('product/<int:product_id>/review/', login_required(views.product_review), name='product_review'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
