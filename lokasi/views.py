from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from lokasi.models import Lokasi

@login_required 
def daftar_lokasi_json(request):
    lokasi_list = list(
        Lokasi.objects.values('id', 'nama_tempat', 'alamat_lengkap', 'latitude', 'longitude')
    )
    return JsonResponse(lokasi_list, safe=False)