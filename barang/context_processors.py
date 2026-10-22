from .models import Wishlist


def navbar(request):
    """Data kecil yang dibutuhkan navbar di semua halaman."""
    if request.user.is_authenticated:
        return {'jumlah_wishlist': Wishlist.objects.filter(user=request.user).count()}
    return {'jumlah_wishlist': 0}
