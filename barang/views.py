from django.shortcuts import render

from .models import Barang


def katalog(request):
    barang_list = (
        Barang.objects.filter(status=Barang.Status.TERSEDIA)
        .select_related('pemilik')
        .prefetch_related('foto')
    )
    return render(request, 'barang/katalog.html', {
        'barang_list': barang_list,
        'total': len(barang_list),
        'nav_aktif': 'katalog',
    })
