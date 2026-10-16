from django import forms

from .models import Barang, FotoBarang

MAKS_FOTO = 5
MAKS_UKURAN_FOTO = 5 * 1024 * 1024

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleImageField(forms.ImageField):
    """ImageField yang menerima beberapa file sekaligus."""

    def __init__(self, *args, **kwargs):
            kwargs.setdefault('widget', MultipleFileInput())
            super().__init__(*args, **kwargs)
    
    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_clean(d, initial) for d in data if d]
        return [single_clean(data, initial)] if data else []

class BarangForm(forms.ModelForm):
    harga = forms.CharField(required=False)
    foto = MultipleImageField(
        required=False,
        widget=MultipleFileInput(attrs={'accept': 'image/jpeg,image/png', 'class': 'visually-hidden'}),
        error_messages={'invalid_image': 'File harus berupa gambar JPG atau PNG.'},
    )

    class Meta:
        model = Barang
        fields = ['judul', 'kategori', 'kondisi', 'tipe', 'harga', 'deskripsi']
        widgets = {
            'judul': forms.TextInput(attrs={'placeholder': 'Contoh: Rak buku kayu 4 susun'}),
            'tipe': forms.RadioSelect,
            'deskripsi': forms.Textarea(
                attrs={'rows': 5, 'maxlength': 500,
                       'placeholder': 'Ceritakan kondisi, ukuran, dan detail penting lainnya...'}
            ),
        }
        error_messages = {
            'judul': {'required': 'Judul wajib diisi.'},
            'kategori': {'required': 'Pilih kategori barang.'},
            'kondisi': {'required': 'Pilih kondisi barang.'},
            'tipe': {'required': 'Pilih tipe transaksi.'},
            'deskripsi': {'required': 'Deskripsi wajib diisi.'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kategori'].choices = [('', 'Pilih kategori')] + list(Barang.Kategori.choices)
        self.fields['kondisi'].choices = [('', 'Pilih kondisi')] + list(Barang.Kondisi.choices)
        self.fields['tipe'].choices = list(Barang.Tipe.choices)
        if not self.is_bound:
            if self.instance.pk and self.instance.harga:
                self.initial['harga'] = f'{self.instance.harga:,}'.replace(',', '.')
            elif not self.instance.pk:
                self.initial.setdefault('tipe', Barang.Tipe.JUAL)
                self.initial['harga'] = ''

    @property
    def foto_lama(self):
        if self.instance.pk:
            return list(self.instance.foto.all())
        return []

    def foto_dihapus_ids(self):
        if not self.is_bound:
            return set()
        ids = set()
        for value in self.data.getlist('hapus_foto'):
            if str(value).isdigit():
                ids.add(int(value))
        return ids

    def clean_judul(self):
        return self.cleaned_data['judul'].strip()

    def clean_harga(self):
        raw = (self.cleaned_data.get('harga') or '').replace('.', '').replace(',', '').strip()
        if not raw:
            return 0
        if not raw.isdigit():
            raise forms.ValidationError('Harga hanya boleh berisi angka.')
        return int(raw)

    def clean_foto(self):
        files = self.cleaned_data.get('foto') or []
        for f in files:
            if f.size > MAKS_UKURAN_FOTO:
                raise forms.ValidationError(f'"{f.name}" lebih dari 5 MB.')
        return files

    def clean(self):
        cleaned = super().clean()
        tipe = cleaned.get('tipe')
        harga = cleaned.get('harga') or 0

        if tipe == Barang.Tipe.JUAL and harga <= 0:
            self.add_error('harga', 'Harga wajib diisi untuk barang yang dijual.')
        if tipe == Barang.Tipe.DONASI:
            cleaned['harga'] = 0

        if 'foto' not in self.errors:
            dihapus = self.foto_dihapus_ids()
            sisa = [f for f in self.foto_lama if f.pk not in dihapus]
            total = len(sisa) + len(cleaned.get('foto') or [])
            if total == 0:
                self.add_error('foto', 'Unggah minimal 1 foto barang.')
            elif total > MAKS_FOTO:
                self.add_error('foto', f'Maksimal {MAKS_FOTO} foto per barang.')
        return cleaned

    def save(self, commit=True):
        barang = super().save(commit=commit)
        if commit:
            self.simpan_foto(barang)
        return barang

    def simpan_foto(self, barang):
        dihapus = self.foto_dihapus_ids()
        if dihapus:
            for foto in barang.foto.filter(pk__in=dihapus):
                foto.delete()
        urutan = barang.foto.count()
        for f in self.cleaned_data.get('foto') or []:
            FotoBarang.objects.create(barang=barang, gambar=f, urutan=urutan)
            urutan += 1
        for i, foto in enumerate(barang.foto.all()):
            if foto.urutan != i:
                foto.urutan = i
                foto.save(update_fields=['urutan'])


class StatusForm(forms.Form):
    status = forms.ChoiceField(choices=Barang.Status.choices)