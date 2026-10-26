from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# model data profil tambahan untuk setiap pengguna ecoswap
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nomor_telepon = models.CharField(max_length=20, blank=True, null=True)
    fakultas = models.CharField(max_length=100, blank=True, null=True)
    domisili = models.CharField(max_length=150, blank=True, null=True)
    foto_profil = models.ImageField(upload_to='profil_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"profil milik {self.user.username}"

# sinyal otomatis: setiap kali ada user baru mendaftar, otomatis buatkan profilnya
@receiver(post_save, sender=User)
def buat_profil_otomatis(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# sinyal otomatis: simpan profil saat data user diperbarui
@receiver(post_save, sender=User)
def simpan_profil_otomatis(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

# model transaksi barter / ajukan minat antar pengguna ecoswap
class Transaksi(models.Model):
    # pilihan status alur transaksi sesuai linimasa modul
    STATUS_CHOICES = [
        ('diajukan', 'Diajukan'),
        ('diterima', 'Diterima'),
        ('ditolak', 'Ditolak'),
        ('dibatalkan', 'Dibatalkan'),
        ('selesai', 'Selesai'),
    ]

    barang = models.ForeignKey('barang.Barang', on_delete=models.CASCADE, related_name='daftar_transaksi')
    pemohon = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaksi_diajukan')
    pemilik = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaksi_masuk')
    pesan = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='diajukan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"transaksi {self.barang} ({self.status}) oleh {self.pemohon.username}"