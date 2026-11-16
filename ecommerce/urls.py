from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts import views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/admin/", include("accounts.api_urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("quan-tri/", views.admin_dashboard, name="admin_dashboard"),
    path("quan-tri/nguoi-dung/", views.admin_users, name="admin_users"),
    path("quan-tri/nguoi-dung/<int:user_id>/sua/", views.admin_customer_edit, name="admin_customer_edit"),
    path("quan-tri/nguoi-dung/<int:user_id>/xoa/", views.admin_customer_delete, name="admin_customer_delete"),
    path("quan-tri/don-hang/<int:order_id>/", views.admin_update_order, name="admin_update_order"),
    path("quan-tri/san-pham/", views.admin_products, name="admin_products"),
    path("quan-tri/san-pham/them/", views.admin_product_create, name="admin_product_create"),
    path("quan-tri/san-pham/<int:product_id>/sua/", views.admin_product_edit, name="admin_product_edit"),
    path("quan-tri/san-pham/<int:product_id>/xoa/", views.admin_product_delete, name="admin_product_delete"),
    path("quan-tri/danh-muc/", views.admin_categories, name="admin_categories"),
    path("quan-tri/danh-muc/them/", views.admin_category_create, name="admin_category_create"),
    path("quan-tri/danh-muc/<int:category_id>/sua/", views.admin_category_edit, name="admin_category_edit"),
    path("quan-tri/danh-muc/<int:category_id>/xoa/", views.admin_category_delete, name="admin_category_delete"),
    path("", views.home, name="home"),
    path("search/", views.search_products, name="search"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("product/<int:product_id>/review/", views.product_review, name="product_review"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("update-cart/<int:item_id>/", views.update_cart, name="update_cart"),
    path("remove-from-cart/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/product/<int:product_id>/", views.checkout, name="checkout_product"),
    path("checkout/cart/", views.checkout, name="checkout_cart"),
    path("place-order/", views.place_order, name="place_order"),
    path("order-confirmation/<int:order_id>/", views.order_confirmation, name="order_confirmation"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("don-hang/", views.my_orders, name="my_orders"),
    path("don-hang/<int:order_id>/huy/", views.cancel_order, name="cancel_order"),
    path("don-hang/<int:order_id>/mua-lai/", views.reorder, name="reorder"),
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),
    path("confirm-received/<int:order_id>/", views.confirm_received, name="confirm_received"),
    path("review-order/<int:order_id>/", views.review_order, name="review_order"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
