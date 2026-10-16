import io
import os
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Barang, FotoBarang

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
