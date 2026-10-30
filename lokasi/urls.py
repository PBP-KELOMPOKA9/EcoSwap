from django.urls import path
from . import views

app_name = 'lokasi'

urlpatterns = [
    path('json/', views.daftar_lokasi_json, name='daftar_lokasi_json'),
]