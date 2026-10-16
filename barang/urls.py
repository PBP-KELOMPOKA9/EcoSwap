from django.urls import path

from . import views

app_name = 'barang'

urlpatterns = [
    path('', views.katalog, name='katalog'),
    path('barang/tambah/', views.tambah, name='tambah'),
    path('barang/<int:pk>/', views.detail, name='detail'),
    path('barang/<int:pk>/edit/', views.edit, name='edit'),
    path('barang/<int:pk>/hapus/', views.hapus, name='hapus'),
    path('barang/<int:pk>/status/', views.ubah_status, name='ubah_status'),
    path('barang-saya/', views.barang_saya, name='barang_saya'),
]
