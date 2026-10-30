"""
URL configuration for EcoSwap project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from profil.views import (
    login_view, register_view, logout_view, profile_view,
    change_password_view, reset_password_view,
    manajemen_transaksi_view, ajukan_transaksi_view, ubah_status_transaksi_view,
    profile_json_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # halaman beranda dan katalog buatan najwa
    path('', include('barang.urls')),

    # fitur chat dan notifikasi
    path('chat/', include('chat.urls')),

    # halaman login, register, logout, dan profil
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profil/', profile_view, name='profile'),
    path('profil/ganti-password/', change_password_view, name='change_password'),
    path('profil/reset-password/', reset_password_view, name='reset_password'),
    path('profil/json/', profile_json_view, name='profile_json'),

    # manajemen transaksi dan barter
    path('transaksi/', manajemen_transaksi_view, name='manajemen_transaksi'),
    path('transaksi/ajukan/<int:barang_id>/', ajukan_transaksi_view, name='ajukan_transaksi'),
    path('transaksi/status/<int:transaksi_id>/<str:aksi>/', ubah_status_transaksi_view, name='ubah_status_transaksi'),

    # ulasan dan lokasi
    path('ulasan/', include('ulasan.urls')),
    path('lokasi/', include('lokasi.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)