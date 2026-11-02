"""Compatibility URL module; the project routes are defined in ecommerce.urls."""

from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="accounts_login"),
    path("register/", views.register_view, name="accounts_register"),
    path("cart/", views.cart, name="accounts_cart"),
]
