import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Transaksi

# fungsi bantuan untuk memvalidasi kekuatan kata sandi (minimal 8 karakter dan bervariasi/unik)
def validasi_kata_sandi(password, username=None):
    if len(password) < 8:
        return False, 'kata sandi minimal 8 karakter!'
    if password.isnumeric():
        return False, 'kata sandi tidak boleh hanya berupa angka! gunakan kombinasi huruf dan angka.'
    if password.isalpha():
        return False, 'kata sandi harus mengandung kombinasi angka agar unik dan kuat!'
    # cek variasi karakter agar tidak mengulang satu karakter yang sama
    if len(set(password)) < 4:
        return False, 'kata sandi terlalu sederhana! gunakan karakter yang lebih unik dan bervariasi.'
    if username and password.lower() == username.lower():
        return False, 'kata sandi tidak boleh sama dengan username!'
    return True, ''

# fungsi untuk memproses login pengguna
def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username')
        password = request.POST.get('password')

        # coba cari user apakah dia mengetik username atau email
        username_to_auth = identifier
        if '@' in identifier:
            user_by_email = User.objects.filter(email=identifier).first()
            if user_by_email:
                username_to_auth = user_by_email.username

        # verifikasi kata sandi ke database django
        user = authenticate(request, username=username_to_auth, password=password)

        if user is not None:
            # berhasil login, simpan sesi
            login(request, user)
            # arahkan langsung ke halaman beranda katalog
            return redirect('/')
        else:
            # gagal login, tampilkan pesan peringatan
            messages.error(request, 'username/email atau password salah!')
            return render(request, 'login.html')

    return render(request, 'login.html')

# fungsi untuk memproses pendaftaran akun baru
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # validasi: cek apakah konfirmasi password cocok
        if password != confirm_password:
            messages.error(request, 'password dan konfirmasi password tidak cocok!')
            return render(request, 'register.html')

        # validasi: cek syarat kata sandi minimal 8 karakter dan unik
        is_valid, error_msg = validasi_kata_sandi(password, username=username)
        if not is_valid:
            messages.error(request, error_msg)
            return render(request, 'register.html')

        # validasi: cek apakah username sudah terpakai
        if User.objects.filter(username=username).exists():
            messages.error(request, 'username ini sudah terpakai, gunakan yang lain!')
            return render(request, 'register.html')

        # buat akun baru dan simpan ke database
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # beri pesan sukses lalu pindahkan ke halaman login
        messages.success(request, 'akun berhasil dibuat! silakan masuk.')
        return redirect('login')

    return render(request, 'register.html')

# fungsi untuk keluar akun (logout)
def logout_view(request):
    logout(request)
    return redirect('/')

# fungsi untuk menampilkan dan memperbarui halaman profil pengguna
@login_required(login_url='/login/')
def profile_view(request):
    # ambil atau buat profil otomatis untuk user yang sedang aktif
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        nomor_telepon = request.POST.get('nomor_telepon', '').strip()

        # validasi nomor whatsapp jika diisi
        if nomor_telepon:
            # bersihkan spasi atau tanda hubung
            clean_phone = nomor_telepon.replace(' ', '').replace('-', '')
            # validasi: harus angka, diawali 08 atau 62, dan panjang 10-14 digit
            if not re.match(r'^(\+62|62|08)[0-9]{8,12}$', clean_phone):
                messages.error(request, 'nomor whatsapp tidak valid! harus berupa angka diawali 08 atau 62 (contoh: 081234567890).')
                return render(request, 'profile.html', {'profile': profile})
            nomor_telepon = clean_phone

        # simpan pembaruan nama dan email ke model user
        request.user.first_name = request.POST.get('first_name', request.user.first_name).strip()
        request.user.email = request.POST.get('email', request.user.email).strip()
        request.user.save()

        # simpan data tambahan ke model userprofile
        profile.nomor_telepon = nomor_telepon
        profile.domisili = request.POST.get('domisili', profile.domisili).strip()
        profile.bio = request.POST.get('bio', profile.bio).strip()

        # simpan foto profil jika ada berkas yang diunggah
        if 'foto_profil' in request.FILES:
            profile.foto_profil = request.FILES['foto_profil']

        profile.save()
        messages.success(request, 'profil berhasil diperbarui!')
        return redirect('profile')

    return render(request, 'profile.html', {'profile': profile})

# fungsi untuk memproses perubahan kata sandi pengguna
@login_required(login_url='/login/')
def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # validasi: cek apakah kata sandi lama sudah benar
        if not request.user.check_password(old_password):
            messages.error(request, 'kata sandi lama kamu salah!')
            return redirect('profile')

        # validasi: cek apakah konfirmasi kata sandi baru cocok
        if new_password != confirm_password:
            messages.error(request, 'konfirmasi kata sandi baru tidak cocok!')
            return redirect('profile')

        # validasi: pastikan kata sandi baru memenuhi syarat minimal 8 karakter dan unik
        is_valid, error_msg = validasi_kata_sandi(new_password, username=request.user.username)
        if not is_valid:
            messages.error(request, error_msg)
            return redirect('profile')

        # simpan kata sandi baru ke database django
        request.user.set_password(new_password)
        request.user.save()

        # perbarui sesi login agar pengguna tidak otomatis keluar (logout)
        update_session_auth_hash(request, request.user)

        messages.success(request, 'kata sandi berhasil diperbarui!')
        return redirect('profile')

    return redirect('profile')

# fungsi untuk mereset kata sandi jika pengguna lupa kata sandi
def reset_password_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # cari akun pengguna berdasarkan username dan email
        user = User.objects.filter(username=username, email__iexact=email).first()
        if not user:
            messages.error(request, 'username dan email tidak cocok dengan data akun manapun!')
            return redirect('login')

        # validasi: pastikan konfirmasi kata sandi cocok
        if new_password != confirm_password:
            messages.error(request, 'konfirmasi kata sandi baru tidak cocok!')
            return redirect('login')

        # validasi: pastikan kata sandi baru minimal 8 karakter dan unik
        is_valid, error_msg = validasi_kata_sandi(new_password, username=user.username)
        if not is_valid:
            messages.error(request, error_msg)
            return redirect('login')

        # simpan kata sandi baru dan berikan notifikasi sukses
        user.set_password(new_password)
        user.save()

        messages.success(request, 'kata sandi berhasil diatur ulang! silakan masuk dengan kata sandi baru.')
        return redirect('login')

    return redirect('login')

# fungsi untuk menampilkan dasbor daftar transaksi pengguna
@login_required(login_url='/login/')
def manajemen_transaksi_view(request):
    permintaan_masuk = Transaksi.objects.filter(pemilik=request.user).order_by('-created_at')
    pengajuan_saya = Transaksi.objects.filter(pemohon=request.user).order_by('-created_at')

    # hitung data metrik untuk kartu ringkasan kpi dashboard
    total_transaksi = permintaan_masuk.count() + pengajuan_saya.count()
    menunggu_respon = permintaan_masuk.filter(status='diajukan').count() + pengajuan_saya.filter(status='diajukan').count()
    siap_barter = permintaan_masuk.filter(status='diterima').count() + pengajuan_saya.filter(status='diterima').count()
    selesai_barter = permintaan_masuk.filter(status='selesai').count() + pengajuan_saya.filter(status='selesai').count()

    context = {
        'permintaan_masuk': permintaan_masuk,
        'pengajuan_saya': pengajuan_saya,
        'total_transaksi': total_transaksi,
        'menunggu_respon': menunggu_respon,
        'siap_barter': siap_barter,
        'selesai_barter': selesai_barter,
        'nav_aktif': 'transaksi',
    }
    return render(request, 'transaksi.html', context)

# fungsi untuk mengajukan minat atau tawaran barter pada suatu barang
@login_required(login_url='/login/')
def ajukan_transaksi_view(request, barang_id):
    from barang.models import Barang
    barang = get_object_or_404(Barang, pk=barang_id)

    # cari pemilik barang secara fleksibel
    pemilik_barang = getattr(barang, 'penjual', getattr(barang, 'pemilik', getattr(barang, 'user', None)))

    # ambil nama barang untuk keperluan notifikasi pesan
    nama_barang = getattr(barang, 'nama', getattr(barang, 'nama_barang', getattr(barang, 'judul', 'barang')))

    # validasi: pemilik dilarang mengajukan transaksi ke barang miliknya sendiri
    if pemilik_barang == request.user:
        messages.error(request, 'kamu tidak bisa mengajukan barter ke barang milikmu sendiri!')
        return redirect('manajemen_transaksi')

    # validasi: cegah pengajuan ganda jika transaksi sebelumnya masih berjalan
    transaksi_berjalan = Transaksi.objects.filter(
        barang=barang, 
        pemohon=request.user, 
        status__in=['diajukan', 'diterima']
    ).exists()
    if transaksi_berjalan:
        messages.error(request, f'kamu sudah memiliki transaksi aktif untuk barang "{nama_barang}"!')
        return redirect('manajemen_transaksi')

    # ambil pesan penawaran jika ada, atau gunakan pesan ramah bawaan
    pesan = request.POST.get('pesan', request.GET.get('pesan', '')).strip()
    if not pesan:
        pesan = f'halo! saya berminat untuk barter/mengambil barang "{nama_barang}".'

    # buat data transaksi baru secara langsung (mendukung tombol link get maupun form post)
    Transaksi.objects.create(
        barang=barang,
        pemohon=request.user,
        pemilik=pemilik_barang,
        pesan=pesan,
        status='diajukan'
    )

    messages.success(request, f'berhasil mengajukan minat untuk "{nama_barang}"! transaksi kamu sudah tercatat di sini.')
    return redirect('manajemen_transaksi')

# fungsi untuk mengubah status transaksi (terima, tolak, batalkan, selesai)
@login_required(login_url='/login/')
def ubah_status_transaksi_view(request, transaksi_id, aksi):
    transaksi = get_object_or_404(Transaksi, pk=transaksi_id)

    # aksi terima tawaran: hanya bisa dilakukan oleh pemilik barang
    if aksi == 'terima' and transaksi.pemilik == request.user:
        transaksi.status = 'diterima'
        transaksi.save()
        messages.success(request, 'tawaran barter berhasil kamu terima! hubungi pemohon via whatsapp untuk serah terima barang.')

    # aksi tolak tawaran: hanya bisa dilakukan oleh pemilik barang
    elif aksi == 'tolak' and transaksi.pemilik == request.user:
        transaksi.status = 'ditolak'
        transaksi.save()
        messages.success(request, 'tawaran barter telah ditolak.')

    # aksi batalkan pengajuan: hanya bisa dilakukan oleh pemohon
    elif aksi == 'batalkan' and transaksi.pemohon == request.user:
        transaksi.status = 'dibatalkan'
        transaksi.save()
        messages.success(request, 'pengajuan barter telah dibatalkan.')

    # aksi selesai: barang sudah berhasil diserahterimakan
    elif aksi == 'selesai' and (transaksi.pemilik == request.user or transaksi.pemohon == request.user):
        transaksi.status = 'selesai'
        transaksi.save()
        messages.success(request, 'transaksi barter selesai! terima kasih sudah mendukung gerakan ramah lingkungan.')

    return redirect('manajemen_transaksi')

# fungsi untuk mengembalikan data profil pengguna dalam format json 
@login_required(login_url='/login/')
def profile_json_view(request):
    user = request.user
    profile = getattr(user, 'profile', None)

    data = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'nomor_telepon': profile.nomor_telepon if profile else '',
        'domisili': profile.domisili if profile else '',
        'bio': profile.bio if profile else '',
    }
    return JsonResponse(data)