from .models import Cart

def cart_context(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return {
            'cart_count': cart.books.count(),
            'cart_items': cart.books.all()
        }
    return {
        'cart_count': 0,
        'cart_items': []
    }