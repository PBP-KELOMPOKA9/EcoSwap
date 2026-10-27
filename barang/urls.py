from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'barang'

urlpatterns = [
    path('', views.home, name='home'),
    path('katalog', views.katalog, name='katalog'),
    path('barang/tambah/', views.tambah, name='tambah'),
    path('barang/<int:pk>/', views.detail, name='detail'),
    path('barang/<int:pk>/edit/', views.edit, name='edit'),
    path('barang/<int:pk>/hapus/', views.hapus, name='hapus'),
    path('barang/<int:pk>/status/', views.ubah_status, name='ubah_status'),
    path('barang-saya/', views.barang_saya, name='barang_saya'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/<int:pk>/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
    path('test-404/', TemplateView.as_view(template_name='404.html'), name='test_404'),
]
