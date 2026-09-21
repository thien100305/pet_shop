from django import template

register = template.Library()

@register.filter
def filter_status(orders, status):
    return [order for order in orders if order.status == status]

@register.filter
def has_review(order_items):
    return all(item.review for item in order_items) 