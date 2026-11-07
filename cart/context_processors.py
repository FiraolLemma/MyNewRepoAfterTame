# cart/context_processors.py
from .models import Cart

def cart_item_count(request):
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                count = cart.items.count()
        else:
            # Ensure session exists before accessing session_key
            if not request.session.session_key:
                request.session.create()  # Create session if it doesn't exist
            cart = Cart.objects.filter(session_key=request.session.session_key).first()
            if cart:
                count = cart.items.count()
    except Exception:
        # If anything goes wrong, return 0 to avoid breaking the template
        count = 0
    
    return {'cart_item_count': count}