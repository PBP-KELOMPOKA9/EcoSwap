from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.daftar_percakapan, name='daftar'),
    path('barang/<int:barang_id>/', views.mulai_percakapan, name='mulai'),
    path('<int:percakapan_id>/pesan/', views.ambil_pesan, name='ambil_pesan'),
    path('<int:percakapan_id>/', views.detail_percakapan, name='detail'),
    path('notifikasi/<int:notifikasi_id>/dibaca/', views.tandai_notifikasi_dibaca, name='tandai_dibaca'),
]