from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api import CategoryViewSet, CustomerViewSet, DashboardAPIView, OrderViewSet, ProductViewSet, ReviewViewSet


router = DefaultRouter()
router.register("products", ProductViewSet, basename="admin-api-products")
router.register("categories", CategoryViewSet, basename="admin-api-categories")
router.register("orders", OrderViewSet, basename="admin-api-orders")
router.register("customers", CustomerViewSet, basename="admin-api-customers")
router.register("reviews", ReviewViewSet, basename="admin-api-reviews")

urlpatterns = [
    path("dashboard/", DashboardAPIView.as_view(), name="admin-api-dashboard"),
    path("", include(router.urls)),
]
