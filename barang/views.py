from EcoSwap import settings
from lokasi.models import Lokasi
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import BarangForm, StatusForm
from .models import Barang, Wishlist

def home(request):
    total_tersedia = Barang.objects.filter(status=Barang.Status.TERSEDIA).count()
    
    # Ambil filter kategori jika ada diklik
    kategori_filter = request.GET.get('kategori', '')
    
    barang_qs = (
        Barang.objects.filter(status=Barang.Status.TERSEDIA)
        .select_related('pemilik')
        .prefetch_related('foto')
    )
    
    if kategori_filter in Barang.Kategori.values:
        barang_qs = barang_qs.filter(kategori=kategori_filter)
        
    # Ambil 8 barang untuk tampilan 2 baris x 4 kolom
    barang_list = barang_qs[:8]
    wishlist_ids = _wishlist_ids(request.user)
    return render(request, 'home.html', {
        'total_tersedia': total_tersedia,
        'barang_list': barang_list,
        'wishlist_ids': wishlist_ids,
        'kategori_filter': kategori_filter,
        'kategori_choices': Barang.Kategori.choices,
        'nav_aktif': 'beranda',
    })

PER_HALAMAN = 12
PILIHAN_URUT = {
    'terbaru': ('Terbaru', ['-created_at']),
    'termurah': ('Termurah', ['harga', '-created_at']),
    'termahal': ('Termahal', ['-harga', '-created_at']),
}


def _wishlist_ids(user):
    if not user.is_authenticated:
        return set()
    return set(Wishlist.objects.filter(user=user).values_list('barang_id', flat=True))


def _redirect_aman(request, fallback):
    tujuan = request.POST.get('next') or request.GET.get('next')
    if tujuan and url_has_allowed_host_and_scheme(tujuan, allowed_hosts={request.get_host()}):
        return redirect(tujuan)
    return redirect(fallback)


def katalog(request):
    qs = (
        Barang.objects.filter(status=Barang.Status.TERSEDIA)
        .select_related('pemilik')
        .prefetch_related('foto')
    )

    q = request.GET.get('q', '').strip()
    kategori_dipilih = [k for k in request.GET.getlist('kategori') if k in Barang.Kategori.values]
    kondisi_dipilih = [k for k in request.GET.getlist('kondisi') if k in Barang.Kondisi.values]
    tipe = request.GET.get('tipe', '')
    if tipe not in Barang.Tipe.values:
        tipe = ''
    urut = request.GET.get('urut', 'terbaru')
    if urut not in PILIHAN_URUT:
        urut = 'terbaru'

    if q:
        qs = qs.filter(Q(judul__icontains=q) | Q(deskripsi__icontains=q))
    if kategori_dipilih:
        qs = qs.filter(kategori__in=kategori_dipilih)
    if kondisi_dipilih:
        qs = qs.filter(kondisi__in=kondisi_dipilih)
    if tipe:
        qs = qs.filter(tipe=tipe)
    qs = qs.order_by(*PILIHAN_URUT[urut][1])

    halaman = Paginator(qs, PER_HALAMAN).get_page(request.GET.get('page'))

    context = {
        'halaman': halaman,
        'barang_list': halaman.object_list,
        'total': halaman.paginator.count,
        'q': q,
        'kategori_choices': Barang.Kategori.choices,
        'kondisi_choices': Barang.Kondisi.choices,
        'tipe_choices': Barang.Tipe.choices,
        'kategori_chip': ['buku', 'furnitur', 'pakaian', 'elektronik'],
        'kategori_dipilih': kategori_dipilih,
        'kondisi_dipilih': kondisi_dipilih,
        'tipe': tipe,
        'urut': urut,
        'pilihan_urut': [(k, v[0]) for k, v in PILIHAN_URUT.items()],
        'urut_label': PILIHAN_URUT[urut][0],
        'ada_filter': bool(q or kategori_dipilih or kondisi_dipilih or tipe),
        'wishlist_ids': _wishlist_ids(request.user),
        'nav_aktif': 'katalog',
    }
    return render(request, 'barang/katalog.html', context)


def detail(request, pk):
    barang = get_object_or_404(
        Barang.objects.select_related('pemilik').prefetch_related('foto'), pk=pk
    )
    is_pemilik = request.user.is_authenticated and request.user == barang.pemilik

    if not is_pemilik:
        Barang.objects.filter(pk=barang.pk).update(jumlah_dilihat=F('jumlah_dilihat') + 1)

    serupa = (
        Barang.objects.filter(kategori=barang.kategori, status=Barang.Status.TERSEDIA)
        .exclude(pk=barang.pk)
        .select_related('pemilik')
        .prefetch_related('foto')[:4]
    )

    # Jembatan ke Modul 4 (Ulasan): ringkasan ulasan barang ini dan rating pemiliknya.
    ulasan_qs = barang.daftar_ulasan.select_related('user')
    ringkasan = ulasan_qs.aggregate(rata=Avg('rating'), total=Count('id'))
    rating_pemilik = Barang.objects.filter(pemilik=barang.pemilik).aggregate(
        rata=Avg('daftar_ulasan__rating'), total=Count('daftar_ulasan')
    )

    context = {
        'barang': barang,
        'fotos': list(barang.foto.all()),
        'ulasan_rata': round(ringkasan['rata'], 1) if ringkasan['rata'] else None,
        'ulasan_bintang': round(ringkasan['rata'] or 0),
        'ulasan_total': ringkasan['total'],
        'ulasan_terbaru': ulasan_qs.order_by('-tanggal_dibuat')[:3],
        'pemilik_rating': round(rating_pemilik['rata'], 1) if rating_pemilik['rata'] else None,
        'pemilik_total_ulasan': rating_pemilik['total'],
        'is_pemilik': is_pemilik,
        'serupa': serupa,
        'wishlist_ids': _wishlist_ids(request.user),
        'status_choices': Barang.Status.choices,
        'nav_aktif': 'barang_saya' if is_pemilik else 'katalog',
    }
    return render(request, 'barang/detail.html', context)


@login_required
def tambah(request):
    if request.method == 'POST':
        form = BarangForm(request.POST, request.FILES)
        if form.is_valid():
            barang = form.save(commit=False)
            barang.pemilik = request.user
            
            nama_tempat = request.POST.get('nama_tempat', '').strip()
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            alamat = request.POST.get('alamat_lengkap', '').strip()
            if nama_tempat and lat and lng:
                lokasi_obj, _ = Lokasi.objects.get_or_create(
                    nama_tempat=nama_tempat,
                    latitude=float(lat),
                    longitude=float(lng),
                    defaults={'alamat_lengkap': alamat}
                )
                barang.lokasi = lokasi_obj
            barang.save()
            form.simpan_foto(barang)
            messages.success(request, f'"{barang.judul}" berhasil ditambahkan ke katalog.')
            return redirect(barang)
    else:
        form = BarangForm()
    return render(request, 'barang/form.html', {
        'form': form,
        'mode': 'tambah',
        'nav_aktif': 'tambah',
        'api_key': settings.GOOGLE_MAPS_API_KEY,
    })


@login_required
def edit(request, pk):
    barang = get_object_or_404(Barang, pk=pk, pemilik=request.user)
    if request.method == 'POST':
        form = BarangForm(request.POST, request.FILES, instance=barang)
        if form.is_valid():
            barang = form.save(commit=False)
            
            nama_tempat = request.POST.get('nama_tempat', '').strip()
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            alamat = request.POST.get('alamat_lengkap', '').strip()
            if nama_tempat:
                try:
                    lat_val = float(lat) if lat else -6.3685
                    lng_val = float(lng) if lng else 106.8245
                except (ValueError, TypeError):
                    lat_val, lng_val = -6.3685, 106.8245

                lokasi_obj, _ = Lokasi.objects.get_or_create(
                    nama_tempat=nama_tempat,
                    latitude=lat_val,
                    longitude=lng_val,
                    defaults={'alamat_lengkap': alamat}
                )
                barang.lokasi = lokasi_obj

                
            barang.save()
            messages.success(request, 'Perubahan berhasil disimpan.')
            return redirect(barang)
    else:
        form = BarangForm(instance=barang)
    return render(request, 'barang/form.html', {
        'form': form,
        'barang': barang,
        'mode': 'edit',
        'nav_aktif': 'barang_saya',
        'api_key': settings.GOOGLE_MAPS_API_KEY,
    })


@login_required
@require_POST
def hapus(request, pk):
    barang = get_object_or_404(Barang, pk=pk, pemilik=request.user)
    judul = barang.judul
    # Hapus foto satu-satu supaya file gambarnya ikut terhapus.
    for foto in barang.foto.all():
        foto.delete()
    barang.delete()
    messages.success(request, f'"{judul}" sudah dihapus.')
    return _redirect_aman(request, 'barang:barang_saya')


@login_required
@require_POST
def ubah_status(request, pk):
    barang = get_object_or_404(Barang, pk=pk, pemilik=request.user)
    form = StatusForm(request.POST)
    if form.is_valid():
        barang.status = form.cleaned_data['status']
        barang.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Status diubah menjadi {barang.get_status_display()}.')
    return redirect(barang)


@login_required
def barang_saya(request):
    semua = Barang.objects.filter(pemilik=request.user)
    hitung = semua.aggregate(
        semua=Count('id'),
        tersedia=Count('id', filter=Q(status=Barang.Status.TERSEDIA)),
        dipesan=Count('id', filter=Q(status=Barang.Status.DIPESAN)),
        selesai=Count('id', filter=Q(status=Barang.Status.SELESAI)),
    )
    status = request.GET.get('status', '')
    qs = semua.prefetch_related('foto')
    if status in Barang.Status.values:
        qs = qs.filter(status=status)
    else:
        status = ''

    tabs = [
        ('', 'Semua', hitung['semua']),
        ('tersedia', 'Tersedia', hitung['tersedia']),
        ('dipesan', 'Dipesan', hitung['dipesan']),
        ('selesai', 'Selesai', hitung['selesai']),
    ]
    return render(request, 'barang/barang_saya.html', {
        'barang_list': qs,
        'tabs': tabs,
        'status_aktif': status,
        'total_semua': hitung['semua'],
        'nav_aktif': 'barang_saya',
    })


@login_required
def wishlist(request):
    items = (
        Wishlist.objects.filter(user=request.user)
        .select_related('barang', 'barang__pemilik')
        .prefetch_related('barang__foto')
    )
    barang_list = [w.barang for w in items]
    return render(request, 'barang/wishlist.html', {
        'barang_list': barang_list,
        'wishlist_ids': {b.pk for b in barang_list},
        'nav_aktif': 'wishlist',
    })


@require_POST
def toggle_wishlist(request, pk):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if not request.user.is_authenticated:
        login_url = f"{reverse('admin:login')}?next={request.POST.get('next', '/')}"
        if is_ajax:
            return JsonResponse({'login_url': login_url}, status=401)
        return redirect(login_url)

    barang = get_object_or_404(Barang, pk=pk)
    item, dibuat = Wishlist.objects.get_or_create(user=request.user, barang=barang)
    if not dibuat:
        item.delete()
    tersimpan = dibuat
    jumlah = Wishlist.objects.filter(user=request.user).count()

    if is_ajax:
        return JsonResponse({'tersimpan': tersimpan, 'jumlah': jumlah})
    if tersimpan:
        messages.success(request, f'"{barang.judul}" disimpan ke wishlist.')
    else:
        messages.success(request, f'"{barang.judul}" dihapus dari wishlist.')
    return _redirect_aman(request, 'barang:katalog')