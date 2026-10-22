import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Barang',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('judul', models.CharField(max_length=100)),
                ('deskripsi', models.TextField(max_length=500)),
                ('kategori', models.CharField(choices=[('buku', 'Buku'), ('furnitur', 'Furnitur'), ('pakaian', 'Pakaian'), ('peralatan_harian', 'Peralatan Harian'), ('elektronik', 'Elektronik'), ('lainnya', 'Lainnya')], max_length=20)),
                ('kondisi', models.CharField(choices=[('baru', 'Baru'), ('seperti_baru', 'Seperti Baru'), ('bekas_baik', 'Bekas Baik'), ('bekas_layak', 'Bekas Layak')], max_length=20)),
                ('tipe', models.CharField(choices=[('donasi', 'Donasi'), ('jual', 'Jual')], max_length=10)),
                ('harga', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('tersedia', 'Tersedia'), ('dipesan', 'Dipesan'), ('selesai', 'Selesai')], default='tersedia', max_length=10)),
                ('lokasi', models.CharField(blank=True, max_length=100)),
                ('jumlah_dilihat', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pemilik', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='barang_dimiliki', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'barang',
                'verbose_name_plural': 'barang',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='FotoBarang',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gambar', models.ImageField(upload_to='barang/%Y/%m/')),
                ('urutan', models.PositiveSmallIntegerField(default=0)),
                ('barang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foto', to='barang.barang')),
            ],
            options={
                'verbose_name': 'foto barang',
                'verbose_name_plural': 'foto barang',
                'ordering': ['urutan', 'id'],
            },
        ),
    ]
