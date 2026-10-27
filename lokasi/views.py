from EcoSwap import settings
from lokasi.models import Lokasi
from django.shortcuts import render

# Create your views here.

def peta_lokasi(request):
    daftar_lokasi = Lokasi.objects.all()
    context = {
        'api_key': settings.GOOGLE_MAPS_API_KEY,
        'daftar_lokasi': daftar_lokasi,
    }
    return render(request, 'lokasi/peta.html', context)


def peta_semua_barang(request):
    daftar_lokasi = Lokasi.objects.all()
    context = {
        'api_key': settings.GOOGLE_MAPS_API_KEY,
        'daftar_lokasi': daftar_lokasi,
    }
    return render(request, 'lokasi/peta.html', context)