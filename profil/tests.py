from django.test import TestCase, Client
from django.contrib.auth.models import User
from profil.models import UserProfile, Transaksi

# kelas pengujian otomatis untuk modul 2: profil, autentikasi, dan transaksi
class ProfilDanAutentikasiTest(TestCase):
    def setUp(self):
        # buat client uji dan user awal untuk pengujian fitur login dan profil
        self.client = Client()
        self.user = User.objects.create_user(
            username='naylatest',
            email='nayla@mail.com',
            password='PasswordAman123'
        )

    # 1. tes registrasi: password kurang dari 8 karakter harus ditolak
    def test_register_password_kurang_dari_8(self):
        response = self.client.post('/register/', {
            'username': 'user_pendek',
            'email': 'pendek@mail.com',
            'password': 'abc',
            'confirm_password': 'abc'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='user_pendek').exists())

    # 2. tes registrasi: password hanya angka (tidak unik/kombinasi) harus ditolak
    def test_register_password_hanya_angka(self):
        response = self.client.post('/register/', {
            'username': 'user_angka',
            'email': 'angka@mail.com',
            'password': '1234567890',
            'confirm_password': '1234567890'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='user_angka').exists())

    # 3. tes registrasi: password hanya huruf (tidak ada kombinasi angka) harus ditolak
    def test_register_password_hanya_huruf(self):
        response = self.client.post('/register/', {
            'username': 'user_huruf',
            'email': 'huruf@mail.com',
            'password': 'katasandisaja',
            'confirm_password': 'katasandisaja'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='user_huruf').exists())

    # 4. tes registrasi: password mengulang satu karakter terus (tidak unik) harus ditolak
    def test_register_password_karakter_sama(self):
        response = self.client.post('/register/', {
            'username': 'user_ulang',
            'email': 'ulang@mail.com',
            'password': 'aaaaaaaaaaaa',
            'confirm_password': 'aaaaaaaaaaaa'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='user_ulang').exists())

    # 5. tes registrasi: konfirmasi password beda harus ditolak
    def test_register_konfirmasi_password_tidak_cocok(self):
        response = self.client.post('/register/', {
            'username': 'user_beda',
            'email': 'beda@mail.com',
            'password': 'PasswordBenar123',
            'confirm_password': 'PasswordBeda456'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='user_beda').exists())

    # 6. tes registrasi berhasil: password minimal 8 karakter dan unik (huruf + angka)
    def test_register_berhasil(self):
        response = self.client.post('/register/', {
            'username': 'maba_sukses',
            'email': 'sukses@mail.com',
            'password': 'SandiKuatEco123',
            'confirm_password': 'SandiKuatEco123'
        })
        # berhasil registrasi harus me-redirect (status 302) ke halaman login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='maba_sukses').exists())

    # 7. tes sinyal profil otomatis: begitu user dibuat, userprofile otomatis terbentuk
    def test_sinyal_profil_otomatis(self):
        user_baru = User.objects.create_user(username='tes_sinyal', password='SandiAman123')
        self.assertTrue(hasattr(user_baru, 'profile'))

    # 8. tes login: username dan password benar harus redirect ke beranda
    def test_login_berhasil(self):
        response = self.client.post('/login/', {
            'username': 'naylatest',
            'password': 'PasswordAman123'
        })
        self.assertEqual(response.status_code, 302)

    # 9. tes login via email: pengguna bisa login menggunakan alamat email terdaftar
    def test_login_dengan_email(self):
        response = self.client.post('/login/', {
            'username': 'nayla@mail.com',
            'password': 'PasswordAman123'
        })
        self.assertEqual(response.status_code, 302)

    # 10. tes login gagal: password salah harus ditolak
    def test_login_password_salah(self):
        response = self.client.post('/login/', {
            'username': 'naylatest',
            'password': 'PasswordSalahTotal99'
        })
        self.assertEqual(response.status_code, 200)

    # 11. tes logout: sesi dibersihkan dan dialihkan ke beranda
    def test_logout(self):
        self.client.login(username='naylatest', password='PasswordAman123')
        response = self.client.post('/logout/')
        self.assertEqual(response.status_code, 302)

    # 12. tes ganti password: password baru < 8 karakter harus ditolak
    def test_ganti_password_kurang_dari_8(self):
        self.client.login(username='naylatest', password='PasswordAman123')
        response = self.client.post('/profil/ganti-password/', {
            'old_password': 'PasswordAman123',
            'new_password': 'abc',
            'confirm_password': 'abc'
        })
        self.assertEqual(response.status_code, 302)
        # pastikan password lama masih berlaku
        self.assertTrue(self.user.check_password('PasswordAman123'))

    # 13. tes ganti password: password baru valid (minimal 8 & unik) harus berhasil
    def test_ganti_password_berhasil(self):
        self.client.login(username='naylatest', password='PasswordAman123')
        response = self.client.post('/profil/ganti-password/', {
            'old_password': 'PasswordAman123',
            'new_password': 'SandiBaruKuat999',
            'confirm_password': 'SandiBaruKuat999'
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('SandiBaruKuat999'))

    # 14. tes validasi nomor whatsapp profil: nomor bukan angka/salah format ditolak
    def test_validasi_nomor_wa_salah(self):
        self.client.login(username='naylatest', password='PasswordAman123')
        response = self.client.post('/profil/', {
            'nomor_telepon': 'nomor_ngasal_bukan_angka',
            'domisili': 'Depok',
            'bio': 'Pengguna EcoSwap'
        })
        self.assertEqual(response.status_code, 200)

    # 15. tes dasbor transaksi: hanya bisa diakses setelah login
    def test_halaman_transaksi_terbuka(self):
        self.client.login(username='naylatest', password='PasswordAman123')
        response = self.client.get('/transaksi/')
        self.assertEqual(response.status_code, 200)