from django.db import models
from django.contrib.auth.models import User
from barang.models import Barang 

class Ulasan(models.Model):
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='daftar_ulasan')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # Wajib diisi (1-5)
    komentar = models.TextField(blank=True, null=True)  # Opsional
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='ulasan_disukai', blank=True)

    @property
    def total_likes(self):
        return self.likes.count()

class FotoUlasan(models.Model):
    ulasan = models.ForeignKey(Ulasan, on_delete=models.CASCADE, related_name='foto_terlampir')
    gambar = models.ImageField(upload_to='foto_ulasan/')