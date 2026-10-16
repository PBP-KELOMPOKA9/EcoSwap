from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import BarangForm, StatusForm
from .models import Barang


def _redirect_aman(request, fallback):
    tujuan = request.POST.get('next') or request.GET.get('next')
    if tujuan and url_has_allowed_host_and_scheme(tujuan, allowed_hosts={request.get_host()}):
        return redirect(tujuan)
    return redirect(fallback)


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
