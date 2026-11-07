# cart/views.py
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.contenttypes.models import ContentType
from .models import Cart, CartItem
from django.apps import apps

def _get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart

def add_to_cart(request, app_label, model_name, product_id):
    content_type = get_object_or_404(ContentType, app_label=app_label, model=model_name)
    product = content_type.get_object_for_this_type(pk=product_id)
    cart = _get_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        content_type=content_type,
        object_id=product.id,
        defaults={'quantity': 1}
    )

    if not created:
        item.quantity += 1
        item.save()

    return redirect("cart:cart_detail")

def cart_detail(request):
    cart = _get_cart(request)
    return render(request, "cart/cart_detail.html", {"cart": cart})

def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect("cart:cart_detail")
