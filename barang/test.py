import io
import os
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
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
