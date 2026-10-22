from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Ulasan, FotoUlasan
# Sesuaikan import Barang ini dengan lokasi model kelompokmu
from barang.models import Barang 
from django.core.files.uploadedfile import SimpleUploadedFile

class UlasanTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_pemilik = User.objects.create_user(username='pemilik', password='password123')
        self.user_lain = User.objects.create_user(username='oranglain', password='password123')

        self.barang = Barang.objects.create(
            pemilik=self.user_pemilik,
            judul='Tas Daur Ulang',
            deskripsi='Tas ramah lingkungan yang sangat kuat.',
            kategori='lainnya',
            kondisi='baru',
            tipe='jual',
            harga=50000
        )

        self.ulasan = Ulasan.objects.create(
            user=self.user_pemilik,
            barang=self.barang,
            rating=4,
            komentar='Bagus banget bahannya!'
        )

    def test_read_daftar_ulasan(self):
        """Test apakah halaman daftar ulasan bisa diakses dan menampilkan ulasan"""
        self.client.login(username='oranglain', password='password123')
        response = self.client.get(reverse('ulasan:daftar_ulasan', args=[self.barang.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ulasan/daftar_ulasan.html')
        self.assertContains(response, 'Bagus banget bahannya!')
        self.assertContains(response, '4,0')

    def test_create_ulasan_baru(self):
        """Test user bisa menambahkan ulasan baru via POST"""
        self.client.login(username='oranglain', password='password123')
        
        gambar_dummy = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )

        response = self.client.post(reverse('ulasan:daftar_ulasan', args=[self.barang.id]), {
            'rating': 5,
            'komentar': 'Produk ramah lingkungan terbaik.',
            'gambar': [gambar_dummy]
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Ulasan.objects.count(), 2)
        self.assertEqual(FotoUlasan.objects.count(), 1)

    def test_edit_ulasan_sendiri(self):
        """Test user bisa mengedit ulasannya sendiri"""
        self.client.login(username='pemilik', password='password123')
        response = self.client.post(reverse('ulasan:edit_ulasan', args=[self.ulasan.id]), {
            'rating': 5,
            'komentar': 'Ternyata awet banget!'
        })
        
        self.assertEqual(response.status_code, 302)
        self.ulasan.refresh_from_db()
        self.assertEqual(self.ulasan.rating, 5)
        self.assertEqual(self.ulasan.komentar, 'Ternyata awet banget!')

    def test_tolak_edit_ulasan_orang_lain(self):
        """Test keamanan: user tidak bisa edit ulasan orang lain"""
        self.client.login(username='oranglain', password='password123')
        response = self.client.post(reverse('ulasan:edit_ulasan', args=[self.ulasan.id]), {
            'rating': 1,
            'komentar': 'Niat iseng ngedit'
        })
        
        self.assertEqual(response.status_code, 302)
        self.ulasan.refresh_from_db()
        self.assertEqual(self.ulasan.rating, 4)

    def test_hapus_ulasan_sendiri(self):
        """Test user bisa menghapus ulasannya sendiri"""
        self.client.login(username='pemilik', password='password123')
        response = self.client.get(reverse('ulasan:hapus_ulasan', args=[self.ulasan.id]))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Ulasan.objects.count(), 0)

    def test_ajax_toggle_like(self):
        """Test fitur tombol 'Membantu' menggunakan request JSON (AJAX)"""
        self.client.login(username='oranglain', password='password123')
        
        response_like = self.client.post(
            reverse('ulasan:toggle_like', args=[self.ulasan.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response_like.status_code, 200)
        self.assertTrue(response_like.json()['liked'])
        self.assertEqual(response_like.json()['total_likes'], 1)

        response_unlike = self.client.post(
            reverse('ulasan:toggle_like', args=[self.ulasan.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response_unlike.status_code, 200)
        self.assertFalse(response_unlike.json()['liked'])
        self.assertEqual(response_unlike.json()['total_likes'], 0)