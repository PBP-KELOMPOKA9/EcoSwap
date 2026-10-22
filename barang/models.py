from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse


class Barang(models.Model):
    class Kategori(models.TextChoices):
        BUKU = 'buku', 'Buku'
        FURNITUR = 'furnitur', 'Furnitur'
        PAKAIAN = 'pakaian', 'Pakaian'
        PERALATAN_HARIAN = 'peralatan_harian', 'Peralatan Harian'
        ELEKTRONIK = 'elektronik', 'Elektronik'
        LAINNYA = 'lainnya', 'Lainnya'

    class Kondisi(models.TextChoices):
        BARU = 'baru', 'Baru'
        SEPERTI_BARU = 'seperti_baru', 'Seperti Baru'
        BEKAS_BAIK = 'bekas_baik', 'Bekas Baik'
        BEKAS_LAYAK = 'bekas_layak', 'Bekas Layak'

    class Tipe(models.TextChoices):
        DONASI = 'donasi', 'Donasi'
        JUAL = 'jual', 'Jual'

    class Status(models.TextChoices):
        TERSEDIA = 'tersedia', 'Tersedia'
        DIPESAN = 'dipesan', 'Dipesan'
        SELESAI = 'selesai', 'Selesai'

    pemilik = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='barang_dimiliki',
    )
    judul = models.CharField(max_length=100)
    deskripsi = models.TextField(max_length=500)
    kategori = models.CharField(max_length=20, choices=Kategori.choices)
    kondisi = models.CharField(max_length=20, choices=Kondisi.choices)
    tipe = models.CharField(max_length=10, choices=Tipe.choices)
    harga = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.TERSEDIA
    )
    lokasi = models.CharField(max_length=100, blank=True)
    jumlah_dilihat = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'barang'
        verbose_name_plural = 'barang'

    def __str__(self):
        return self.judul

    def get_absolute_url(self):
        return reverse('barang:detail', args=[self.pk])

    @property
    def is_donasi(self):
        return self.tipe == self.Tipe.DONASI

    @property
    def is_tersedia(self):
        return self.status == self.Status.TERSEDIA

    @property
    def foto_utama(self):
        fotos = list(self.foto.all())
        return fotos[0] if fotos else None


class FotoBarang(models.Model):
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='foto')
    gambar = models.ImageField(upload_to='barang/%Y/%m/')
    urutan = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['urutan', 'id']
        verbose_name = 'foto barang'
        verbose_name_plural = 'foto barang'

    def __str__(self):
        return f'Foto {self.urutan + 1} - {self.barang.judul}'


class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist'
    )
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='wishlist_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'barang'], name='unik_wishlist_per_user'),
        ]

    def __str__(self):
        return f'{self.user} - {self.barang}'


@receiver(post_delete, sender=FotoBarang)
def hapus_file_foto(sender, instance, **kwargs):
    """Hapus file gambar dari storage saat datanya dihapus."""
    if instance.gambar:
        instance.gambar.delete(save=False)


class Lokasi(models.Model):
    nama = models.CharField(max_length=100)
    alamat = models.CharField(max_length=255, blank=True, default="")
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return self.nama