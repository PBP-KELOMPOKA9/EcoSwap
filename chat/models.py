from django.conf import settings
from django.db import models


# Menghubungkan satu barang dengan pembeli dan penjual
class Conversation(models.Model):
    # Barang yang sedang dibicarakan
    barang = models.ForeignKey('barang.Barang', on_delete=models.CASCADE, related_name='percakapan',)

    # Dua pengguna yang terlibat dalam percakapan
    pembeli = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='percakapan_sebagai_pembeli')
    penjual = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='percakapan_sebagai_penjual')

    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diperbarui_pada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-diperbarui_pada']
        constraints = [
            models.UniqueConstraint(
                fields=['barang', 'pembeli'],
                name='unik_percakapan_barang_pembeli',
            ),
        ]

    def __str__(self):
        return f'{self.pembeli} - {self.barang.judul}'


# Menyimpan isi pesan dan siapa pengirimnya
class Message(models.Model):
    # Percakapan tempat pesan ini dikirim
    percakapan = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='pesan')

    # Pengguna yang mengirim pesan
    pengirim = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pesan_chat',)
    isi = models.TextField(max_length=2000)
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    dibaca_pada = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['dibuat_pada']

    def __str__(self):
        return f'Pesan dari {self.pengirim} pada {self.dibuat_pada}'


# Menghubungkan pesan dengan pengguna yang perlu diberi tahu
class Notification(models.Model):
    # Pengguna yang menerima notifikasi
    penerima = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifikasi_chat',)

    # Pesan yang memicu notifikasi
    pesan = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifikasi')
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    sudah_dibaca = models.BooleanField(default=False)

    class Meta:
        ordering = ['-dibuat_pada']
        constraints = [
            models.UniqueConstraint(
                fields=['penerima', 'pesan'],
                name='unik_notifikasi_penerima_pesan',
            ),
        ]

    def __str__(self):
        return f'Notifikasi untuk {self.penerima}'