from django.contrib.auth.decorators import  login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils.dateformat import format as format_date
from django.utils import timezone
from django.views.decorators.http import require_POST

from barang.models import Barang
from .models import Conversation, Message, Notification


@login_required
def daftar_percakapan(request):
    percakapan = Conversation.objects.filter(
        Q(pembeli=request.user) | Q(penjual=request.user)
    ).select_related('barang', 'pembeli', 'penjual')

    notifikasi = Notification.objects.filter(
        penerima=request.user, sudah_dibaca=False,
    ).select_related(
        'pesan__pengirim',
        'pesan__percakapan__barang',
    )[:10]

    jumlah_belum_dibaca = Notification.objects.filter(
        penerima=request.user, sudah_dibaca=False,).count()

    context = {
        'percakapan': percakapan,
        'notifikasi': notifikasi,
        'jumlah_belum_dibaca': jumlah_belum_dibaca
    }

    return render(request, 'chat/daftar_percakapan.html', context)


@login_required
def mulai_percakapan(request, barang_id):
    barang = get_object_or_404(Barang, pk=barang_id)
    if barang.pemilik == request.user:
        return redirect('barang:detail', pk=barang.pk)

    percakapan, dibuat = Conversation.objects.get_or_create(
        barang=barang,
        pembeli=request.user,
        defaults={'penjual': barang.pemilik}
    )

    return redirect('chat:detail', percakapan_id=percakapan.pk,)


@login_required
def ambil_pesan(request, percakapan_id):
    percakapan = get_object_or_404(
        Conversation.objects.filter(
            Q(pembeli=request.user) | Q(penjual=request.user)
        ), pk=percakapan_id,
    )

    pesan_list = percakapan.pesan.select_related(
        'pengirim'
    ).order_by('dibuat_pada')

    data_pesan = [
        {
            'id': pesan.pk,
            'pengirim': pesan.pengirim.username,
            'isi': pesan.isi,
            'waktu': format_date(timezone.localtime(pesan.dibuat_pada), 'H:i'), 'milik_saya': pesan.pengirim_id == request.user.pk
        }
        for pesan in pesan_list
    ]

    return JsonResponse({'pesan': data_pesan})


@login_required
@require_http_methods(['GET', 'POST'])
def detail_percakapan(request, percakapan_id):
    # Pengguna hanya boleh membuka percakapan yang melibatkan dirinya.
    percakapan = get_object_or_404(
        Conversation.objects.select_related(
            'barang', 'pembeli', 'penjual').filter(
                Q(pembeli=request.user) | Q(penjual=request.user)
            ), pk=percakapan_id,
    )

    error = None

    if request.method == 'POST':
        isi = request.POST.get('isi', '').strip()
        is_ajax = (request.headers.get('X-Requested-With') == 'XMLHttpRequest')

        if not isi:
            error = 'Pesan tidak boleh kosong.'
        elif len(isi) > 2000:
            error = 'Pesan maksimal 2000 karakter.'

        if error:
            if is_ajax:
                return JsonResponse({'error': error}, status=400,)
        else:
            # Simpan pesan dengan pengguna yang sedang login sebagai pengirim
            pesan = Message.objects.create(
                percakapan=percakapan,
                pengirim=request.user,
                isi=isi,
            )

            # Tentukan penerima pesan
            if request.user == percakapan.pembeli:
                penerima = percakapan.penjual
            else:
                penerima = percakapan.pembeli

            # Buat notifikasi untuk peserta lainnya
            Notification.objects.create(
                penerima=penerima,
                pesan=pesan,
            )

            percakapan.save()

            # Jika AJAX, kembalikan data pesan dalam bentuk JSON
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'pesan': {
                        'id': pesan.pk,
                        'pengirim': pesan.pengirim.username,
                        'isi': pesan.isi,
                        'waktu': format_date(timezone.localtime(pesan.dibuat_pada), 'H:i',),
                        'milik_saya': True,
                    },
                })

            return redirect('chat:detail', percakapan_id=percakapan.pk,)

    # Ambil pesan untuk ditampilkan, baik pada GET maupun POST
    pesan_list = percakapan.pesan.select_related('pengirim').all()

    percakapan_list = Conversation.objects.filter(
        Q(pembeli=request.user) | Q(penjual=request.user)
    ).select_related('barang', 'pembeli', 'penjual')

    context = {
        'percakapan_list': percakapan_list,
        'percakapan': percakapan,
        'pesan_list': pesan_list,
        'error': error,
    }

    return render(request, 'chat/detail_percakapan.html', context)


@login_required
@require_POST
def tandai_notifikasi_dibaca(request, notifikasi_id):
    notifikasi = get_object_or_404(Notification, pk=notifikasi_id, penerima=request.user,)

    notifikasi.sudah_dibaca = True
    notifikasi.save(update_fields=['sudah_dibaca'])

    jumlah_belum_dibaca = Notification.objects.filter(
        penerima=request.user, sudah_dibaca=False,
    ).count()

    return JsonResponse({
        'success': True,
        'jumlah_belum_dibaca': jumlah_belum_dibaca
    })