import re
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile

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
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # validasi: cek apakah konfirmasi password cocok
        if password != confirm_password:
            messages.error(request, 'password dan konfirmasi password tidak cocok!')
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