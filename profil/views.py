from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages

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