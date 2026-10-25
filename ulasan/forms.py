from django import forms
from .models import Ulasan, FotoUlasan

# 1. Kita buat widget kustom untuk "memaksa" Django menerima multiple files
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class UlasanForm(forms.ModelForm):
    class Meta:
        model = Ulasan
        fields = ['rating', 'komentar']

class FotoUlasanForm(forms.ModelForm):
    # 2. Kita panggil widget kustom tersebut di sini
    gambar = forms.ImageField(
        widget=MultipleFileInput(attrs={'multiple': True}), 
        required=False
    )
    
    class Meta:
        model = FotoUlasan
        fields = ['gambar']