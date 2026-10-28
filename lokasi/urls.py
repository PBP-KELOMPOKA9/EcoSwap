from django.urls import path
from . import views

app_name = 'lokasi'

urlpatterns = [
    path('peta/', views.peta_semua_barang, name='peta'),
]