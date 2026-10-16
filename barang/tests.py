import io
import os
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Barang, FotoBarang, Wishlist

MEDIA_TEST = tempfile.mkdtemp()


def gambar_dummy(nama='foto.png'):
    buf = io.BytesIO()
    Image.new('RGB', (40, 30), (0, 128, 76)).save(buf, format='PNG')
    return SimpleUploadedFile(nama, buf.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT=MEDIA_TEST)
class BarangModelTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEST, ignore_errors=True)

    def setUp(self):
        self.pemilik = get_user_model().objects.create_user('pemilik', password='rahasia123')
        self.barang = Barang.objects.create(
            pemilik=self.pemilik, judul='Rak Buku Kayu', deskripsi='Masih kokoh.',
            kategori='furnitur', kondisi='bekas_baik', tipe='jual', harga=75000,
        )

    def test_default_status_tersedia(self):
        self.assertTrue(self.barang.is_tersedia)
        self.assertFalse(self.barang.is_donasi)

    def test_foto_utama_adalah_foto_pertama(self):
        self.assertIsNone(self.barang.foto_utama)
        pertama = FotoBarang.objects.create(barang=self.barang, gambar=gambar_dummy('a.png'), urutan=0)
        FotoBarang.objects.create(barang=self.barang, gambar=gambar_dummy('b.png'), urutan=1)
        self.assertEqual(self.barang.foto_utama, pertama)

    def test_file_foto_ikut_terhapus(self):
        foto = FotoBarang.objects.create(barang=self.barang, gambar=gambar_dummy())
        path = foto.gambar.path
        self.assertTrue(os.path.exists(path))
        foto.delete()
        self.assertFalse(os.path.exists(path))


class KatalogDasarTest(TestCase):
    def setUp(self):
        pemilik = get_user_model().objects.create_user('pemilik', password='rahasia123')
        self.tersedia = Barang.objects.create(
            pemilik=pemilik, judul='Lampu Belajar', deskripsi='-',
            kategori='elektronik', kondisi='baru', tipe='donasi',
        )
        Barang.objects.create(
            pemilik=pemilik, judul='Kursi Sudah Diambil', deskripsi='-',
            kategori='furnitur', kondisi='baru', tipe='donasi', status='selesai',
        )

    def test_katalog_hanya_barang_tersedia(self):
        res = self.client.get(reverse('barang:katalog'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Lampu Belajar')
        self.assertContains(res, 'Gratis')
        self.assertNotContains(res, 'Kursi Sudah Diambil')
        self.assertContains(res, '1 barang ditemukan')

    def test_katalog_kosong(self):
        Barang.objects.all().delete()
        res = self.client.get(reverse('barang:katalog'))
        self.assertContains(res, 'Katalog masih kosong')

    def test_filter_kategori_tipe_dan_cari(self):
        pemilik = get_user_model().objects.get(username='pemilik')
        Barang.objects.create(pemilik=pemilik, judul='Novel Bekas', deskripsi='-',
                              kategori='buku', kondisi='baru', tipe='jual', harga=20000)
        res = self.client.get(reverse('barang:katalog'), {'kategori': 'buku'})
        self.assertContains(res, 'Novel Bekas')
        self.assertNotContains(res, 'Lampu Belajar')
        res = self.client.get(reverse('barang:katalog'), {'tipe': 'donasi'})
        self.assertContains(res, 'Lampu Belajar')
        self.assertNotContains(res, 'Novel Bekas')
        res = self.client.get(reverse('barang:katalog'), {'q': 'lampu'})
        self.assertContains(res, '1 barang ditemukan')
        res = self.client.get(reverse('barang:katalog'), {'q': 'tidak-ada'})
        self.assertContains(res, 'Barang tidak ditemukan')

    def test_urut_termurah_dan_pagination(self):
        pemilik = get_user_model().objects.get(username='pemilik')
        for i in range(14):
            Barang.objects.create(pemilik=pemilik, judul=f'Buku {i:02d}', deskripsi='-',
                                  kategori='buku', kondisi='baru', tipe='jual', harga=1000 + i)
        res = self.client.get(reverse('barang:katalog'), {'urut': 'termurah'})
        judul = [b.judul for b in res.context['barang_list']]
        self.assertEqual(judul[0], 'Lampu Belajar')
        self.assertEqual(len(judul), 12)
        res = self.client.get(reverse('barang:katalog'), {'urut': 'termurah', 'page': 2})
        self.assertEqual(len(res.context['barang_list']), 3)


@override_settings(MEDIA_ROOT=MEDIA_TEST)
class BarangCrudTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.pemilik = User.objects.create_user('pemilik', password='rahasia123')
        self.pencari = User.objects.create_user('pencari', password='rahasia123')
        self.barang = Barang.objects.create(
            pemilik=self.pemilik, judul='Rak Buku Kayu', deskripsi='Masih kokoh.',
            kategori='furnitur', kondisi='bekas_baik', tipe='jual', harga=75000,
        )
        FotoBarang.objects.create(barang=self.barang, gambar=gambar_dummy())

    def data_form(self, **ubah):
        data = {
            'judul': 'Kipas Angin', 'kategori': 'elektronik', 'kondisi': 'bekas_baik',
            'tipe': 'jual', 'harga': '60.000', 'deskripsi': 'Masih dingin.',
        }
        data.update(ubah)
        return data

    # ---------- Tambah ----------
    def test_tambah_wajib_login(self):
        res = self.client.get(reverse('barang:tambah'))
        self.assertEqual(res.status_code, 302)

    def test_tambah_barang_dengan_foto(self):
        self.client.login(username='pencari', password='rahasia123')
        data = self.data_form()
        data['foto'] = [gambar_dummy('a.png'), gambar_dummy('b.png')]
        res = self.client.post(reverse('barang:tambah'), data)
        baru = Barang.objects.get(judul='Kipas Angin')
        self.assertRedirects(res, baru.get_absolute_url())
        self.assertEqual(baru.pemilik, self.pencari)
        self.assertEqual(baru.harga, 60000)
        self.assertEqual(baru.foto.count(), 2)

    def test_tambah_validasi(self):
        self.client.login(username='pencari', password='rahasia123')
        res = self.client.post(reverse('barang:tambah'), self.data_form(judul='', harga=''))
        self.assertContains(res, 'Judul wajib diisi.')
        self.assertContains(res, 'Harga wajib diisi untuk barang yang dijual.')
        self.assertContains(res, 'Unggah minimal 1 foto barang.')

    def test_donasi_harga_jadi_nol(self):
        self.client.login(username='pencari', password='rahasia123')
        data = self.data_form(tipe='donasi', harga='50.000')
        data['foto'] = gambar_dummy()
        self.client.post(reverse('barang:tambah'), data)
        self.assertEqual(Barang.objects.get(judul='Kipas Angin').harga, 0)

    # ---------- Edit, status, hapus ----------
    def test_edit_hanya_pemilik(self):
        self.client.login(username='pencari', password='rahasia123')
        res = self.client.get(reverse('barang:edit', args=[self.barang.pk]))
        self.assertEqual(res.status_code, 404)

    def test_edit_dan_hapus_foto(self):
        self.client.login(username='pemilik', password='rahasia123')
        foto_lama = self.barang.foto.first()
        data = self.data_form(judul='Rak Buku Jati')
        data['hapus_foto'] = [foto_lama.pk]
        data['foto'] = gambar_dummy('baru.png')
        self.client.post(reverse('barang:edit', args=[self.barang.pk]), data)
        self.barang.refresh_from_db()
        self.assertEqual(self.barang.judul, 'Rak Buku Jati')
        self.assertEqual(self.barang.foto.count(), 1)
        self.assertNotEqual(self.barang.foto.first().pk, foto_lama.pk)

    def test_edit_tidak_boleh_hapus_semua_foto(self):
        self.client.login(username='pemilik', password='rahasia123')
        data = self.data_form()
        data['hapus_foto'] = [self.barang.foto.first().pk]
        res = self.client.post(reverse('barang:edit', args=[self.barang.pk]), data)
        self.assertContains(res, 'Unggah minimal 1 foto barang.')

    def test_ubah_status(self):
        self.client.login(username='pemilik', password='rahasia123')
        self.client.post(reverse('barang:ubah_status', args=[self.barang.pk]), {'status': 'dipesan'})
        self.barang.refresh_from_db()
        self.assertEqual(self.barang.status, 'dipesan')

    def test_hapus_barang(self):
        self.client.login(username='pemilik', password='rahasia123')
        res = self.client.post(reverse('barang:hapus', args=[self.barang.pk]))
        self.assertRedirects(res, reverse('barang:barang_saya'))
        self.assertFalse(Barang.objects.filter(pk=self.barang.pk).exists())

    def test_hapus_butuh_post(self):
        self.client.login(username='pemilik', password='rahasia123')
        res = self.client.get(reverse('barang:hapus', args=[self.barang.pk]))
        self.assertEqual(res.status_code, 405)

    # ---------- Detail ----------
    def test_detail_versi_pemilik_dan_pencari(self):
        self.client.login(username='pemilik', password='rahasia123')
        self.assertContains(self.client.get(self.barang.get_absolute_url()), 'Edit Barang')
        self.client.login(username='pencari', password='rahasia123')
        res = self.client.get(self.barang.get_absolute_url())
        self.assertContains(res, 'Ajukan Minat')
        self.assertNotContains(res, 'Edit Barang')

    def test_detail_menambah_jumlah_dilihat(self):
        self.client.get(self.barang.get_absolute_url())
        self.barang.refresh_from_db()
        self.assertEqual(self.barang.jumlah_dilihat, 1)

    # ---------- Barang Saya ----------
    def test_barang_saya_hanya_milik_sendiri(self):
        self.client.login(username='pencari', password='rahasia123')
        res = self.client.get(reverse('barang:barang_saya'))
        self.assertNotContains(res, 'Rak Buku Kayu')


class WishlistTest(TestCase):
    def setUp(self):
        User = get_user_model()
        pemilik = User.objects.create_user('pemilik', password='rahasia123')
        self.pencari = User.objects.create_user('pencari', password='rahasia123')
        self.barang = Barang.objects.create(
            pemilik=pemilik, judul='Rak Buku Kayu', deskripsi='-',
            kategori='furnitur', kondisi='bekas_baik', tipe='jual', harga=75000,
        )
        self.url = reverse('barang:toggle_wishlist', args=[self.barang.pk])

    def test_toggle_wishlist_ajax(self):
        self.client.login(username='pencari', password='rahasia123')
        res = self.client.post(self.url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.json(), {'tersimpan': True, 'jumlah': 1})
        res = self.client.post(self.url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.json(), {'tersimpan': False, 'jumlah': 0})

    def test_toggle_tanpa_javascript(self):
        self.client.login(username='pencari', password='rahasia123')
        res = self.client.post(self.url, {'next': '/'})
        self.assertRedirects(res, '/')
        self.assertTrue(Wishlist.objects.filter(user=self.pencari, barang=self.barang).exists())

    def test_tamu_diarahkan_login(self):
        res = self.client.post(self.url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.status_code, 401)

    def test_halaman_wishlist(self):
        Wishlist.objects.create(user=self.pencari, barang=self.barang)
        self.client.login(username='pencari', password='rahasia123')
        res = self.client.get(reverse('barang:wishlist'))
        self.assertContains(res, 'Rak Buku Kayu')
        self.assertContains(res, '1 barang tersimpan')

    def test_barang_tidak_tersedia_ditandai(self):
        self.barang.status = 'selesai'
        self.barang.save()
        Wishlist.objects.create(user=self.pencari, barang=self.barang)
        self.client.login(username='pencari', password='rahasia123')
        res = self.client.get(reverse('barang:wishlist'))
        self.assertContains(res, 'Sudah tidak tersedia')

    def test_wishlist_kosong(self):
        self.client.login(username='pencari', password='rahasia123')
        res = self.client.get(reverse('barang:wishlist'))
        self.assertContains(res, 'Belum ada barang favorit')
