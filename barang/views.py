from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import BarangForm, StatusForm
from .models import Barang

PER_HALAMAN = 12
PILIHAN_URUT = {
    'terbaru': ('Terbaru', ['-created_at']),
    'termurah': ('Termurah', ['harga', '-created_at']),
    'termahal': ('Termahal', ['-harga', '-created_at']),
}


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

    context = {
        'barang': barang,
        'fotos': list(barang.foto.all()),
        'is_pemilik': is_pemilik,
        'serupa': serupa,
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
    })


@login_required
def edit(request, pk):
    barang = get_object_or_404(Barang, pk=pk, pemilik=request.user)
    if request.method == 'POST':
        form = BarangForm(request.POST, request.FILES, instance=barang)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perubahan berhasil disimpan.')
            return redirect(barang)
    else:
        form = BarangForm(instance=barang)
    return render(request, 'barang/form.html', {
        'form': form,
        'barang': barang,
        'mode': 'edit',
        'nav_aktif': 'barang_saya',
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
