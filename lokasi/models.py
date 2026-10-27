from django.db import models

# Create your models here.

class Lokasi(models.Model):
    nama_tempat = models.CharField(max_length=150)
    alamat_lengkap = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    def __str__(self):
        return self.nama_tempat