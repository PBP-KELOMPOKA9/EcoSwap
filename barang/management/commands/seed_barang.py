import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from barang.models import Barang

DATA = [
    ('Paket Buku Kuliah Ekonomi', 'buku', 'donasi', 0, 'bekas_baik', 'Beji, Depok',
     'Tiga buku pengantar ekonomi mikro dan makro. Ada sedikit stabilo di beberapa halaman, sisanya bersih.'),
    ('Rak Buku Kayu 4 Susun', 'furnitur', 'jual', 75000, 'bekas_baik', 'Kukusan, Depok',
     'Rak buku kayu empat susun, kokoh dan masih sangat layak pakai. Ada sedikit bekas pemakaian di bagian samping, tetapi tidak mengganggu fungsi. Cocok untuk kamar kos atau ruang belajar.'),
    ('Kemeja Flanel Uniseks', 'pakaian', 'jual', 35000, 'seperti_baru', 'Pondok Cina, Depok',
     'Kemeja flanel ukuran L, baru dipakai dua kali. Warna masih cerah, tidak ada noda.'),
    ('Lampu Meja Belajar', 'elektronik', 'donasi', 0, 'bekas_layak', 'Margonda, Depok',
     'Lampu belajar LED dengan kabel USB. Cahaya masih terang, hanya engsel agak longgar.'),
    ('Set Alat Masak Kos', 'peralatan_harian', 'jual', 45000, 'bekas_baik', 'Kukusan, Depok',
     'Wajan, panci kecil, spatula, dan sendok sayur. Semua dicuci bersih dan siap pakai.'),
    ('Kursi Kayu Minimalis', 'furnitur', 'jual', 65000, 'bekas_baik', 'Srengseng Sawah',
     'Kursi kayu ringan dengan sandaran. Masih kuat, cat sedikit pudar di bagian kaki.'),
    ('Kipas Angin Meja', 'elektronik', 'donasi', 0, 'bekas_layak', 'Beji, Depok',
     'Kipas angin meja 3 kecepatan. Masih berfungsi normal, agak berisik di kecepatan tertinggi.'),
    ('Rice Cooker Mini', 'elektronik', 'jual', 90000, 'seperti_baru', 'Pondok Cina, Depok',
     'Rice cooker 0,6 liter, cocok untuk satu sampai dua orang. Lapisan anti lengket masih mulus.'),
    ('Novel & Buku Bacaan', 'buku', 'donasi', 0, 'bekas_baik', 'Margonda, Depok',
     'Lima novel fiksi berbahasa Indonesia. Halaman lengkap, sampul sedikit menguning.'),
    ('Rak Sepatu Kayu', 'furnitur', 'jual', 50000, 'bekas_layak', 'Kukusan, Depok',
     'Rak sepatu tiga tingkat, muat sekitar sembilan pasang sepatu.'),
    ('Jaket Kampus Navy', 'pakaian', 'jual', 45000, 'bekas_baik', 'Beji, Depok',
     'Jaket hoodie warna navy ukuran M. Resleting lancar, bahan masih tebal.'),
    ('Perlengkapan Dapur', 'peralatan_harian', 'donasi', 0, 'bekas_baik', 'Pondok Cina, Depok',
     'Piring, gelas, dan toples plastik. Dibagikan karena sudah mau pindah kos.'),
    ('Buku Kalkulus Purcell Jilid 1', 'buku', 'jual', 40000, 'seperti_baru', 'Kutek, Depok',
     'Buku kalkulus edisi kesembilan. Bersih tanpa coretan.'),
    ('Meja Lipat Belajar', 'furnitur', 'jual', 55000, 'bekas_baik', 'Kober, Depok',
     'Meja lipat portable, bisa dipakai di kasur atau lantai.'),
    ('Kaos Polos Hitam (3 pcs)', 'pakaian', 'donasi', 0, 'bekas_layak', 'Kukusan, Depok',
     'Tiga kaos polos ukuran M. Sudah dicuci, masih nyaman dipakai.'),
    ('Setrika Listrik', 'elektronik', 'jual', 60000, 'bekas_baik', 'Margonda, Depok',
     'Setrika ringan 350 watt. Panas merata, kabel masih aman.'),
    ('Gantungan Baju Lipat', 'peralatan_harian', 'donasi', 0, 'bekas_layak', 'Kober, Depok',
     'Gantungan baju lipat stainless. Cocok untuk menjemur di kamar kos.'),
    ('Dispenser Galon Atas', 'elektronik', 'jual', 120000, 'bekas_baik', 'Beji, Depok',
     'Dispenser panas dan normal. Bagian dalam sudah dibersihkan.'),
    ('Modul Praktikum Fisika Dasar', 'buku', 'donasi', 0, 'bekas_layak', 'Pondok Cina, Depok',
     'Modul praktikum fisika dasar semester satu. Ada beberapa catatan pensil.'),
    ('Cermin Dinding Bulat', 'lainnya', 'jual', 30000, 'seperti_baru', 'Kukusan, Depok',
     'Cermin bulat diameter 40 cm dengan bingkai kayu.'),
    ('Tas Ransel Laptop', 'lainnya', 'jual', 70000, 'bekas_baik', 'Margonda, Depok',
     'Ransel muat laptop 15 inci, banyak kantong, resleting lengkap.'),
    ('Kotak Penyimpanan Plastik', 'peralatan_harian', 'donasi', 0, 'bekas_baik', 'Kutek, Depok',
     'Dua kotak plastik bertutup ukuran sedang. Cocok untuk merapikan barang di kos.'),
    ('Sweater Rajut Krem', 'pakaian', 'jual', 40000, 'seperti_baru', 'Beji, Depok',
     'Sweater rajut ukuran S, lembut dan tidak berbulu.'),
    ('Kasur Lipat Busa', 'furnitur', 'jual', 85000, 'bekas_baik', 'Kober, Depok',
     'Kasur lipat busa tebal 7 cm, sarung bisa dilepas dan dicuci.'),
]

USERS = [
    ('aulia', 'Aulia', 'Rahma'),
    ('budi', 'Budi', 'Santoso'),
    ('rina', 'Rina', 'Amalia'),
]


class Command(BaseCommand):
    help = 'Isi data dummy barang untuk Modul 1 (tanpa foto, foto ditambahkan manual).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pemilik',
            help='Username yang ikut kebagian sebagian barang (supaya halaman Barang Saya ada isinya).',
        )
        parser.add_argument('--reset', action='store_true', help='Hapus semua barang lama dulu.')

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        if options['reset']:
            Barang.objects.all().delete()

        pemilik_list = []
        for username, first, last in USERS:
            user, dibuat = User.objects.get_or_create(
                username=username, defaults={'first_name': first, 'last_name': last}
            )
            if dibuat:
                user.set_password('ecoswap123')
                user.save()
            pemilik_list.append(user)

        if options.get('pemilik'):
            pemilik_list.append(User.objects.get(username=options['pemilik']))

        random.seed(42)
        for i, (judul, kategori, tipe, harga, kondisi, lokasi, deskripsi) in enumerate(DATA):
            Barang.objects.get_or_create(
                judul=judul,
                defaults={
                    'pemilik': pemilik_list[i % len(pemilik_list)],
                    'kategori': kategori,
                    'tipe': tipe,
                    'harga': harga,
                    'kondisi': kondisi,
                    'lokasi': lokasi,
                    'deskripsi': deskripsi,
                    'jumlah_dilihat': random.randint(3, 40),
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f'Selesai. Total barang: {Barang.objects.count()}. '
            'Akun dummy: aulia / budi / rina (password: ecoswap123).'
        ))
