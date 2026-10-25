from django.urls import path
from . import views

app_name = 'ulasan'

urlpatterns = [
    path('<int:barang_id>/', views.daftar_ulasan, name='daftar_ulasan'),
    path('edit/<int:ulasan_id>/', views.edit_ulasan, name='edit_ulasan'),
    path('hapus/<int:ulasan_id>/', views.hapus_ulasan, name='hapus_ulasan'),
    path('like/<int:ulasan_id>/', views.toggle_like, name='toggle_like'),
]