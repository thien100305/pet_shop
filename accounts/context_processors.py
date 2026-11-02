from django.db.models import Sum

from .models import CartItem


def store_context(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(cart__user=request.user).aggregate(total=Sum("quantity"))["total"] or 0
    return {"cart_count": cart_count}
