from django.contrib import admin

from .models import Barang, FotoBarang


class FotoBarangInline(admin.TabularInline):
    model = FotoBarang
    extra = 0


@admin.register(Barang)
class BarangAdmin(admin.ModelAdmin):
    list_display = ('judul', 'pemilik', 'kategori', 'tipe', 'harga', 'status', 'created_at')
    list_filter = ('kategori', 'tipe', 'kondisi', 'status')
    search_fields = ('judul', 'deskripsi', 'pemilik__username')
    inlines = [FotoBarangInline]
