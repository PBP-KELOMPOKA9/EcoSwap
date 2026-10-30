from django import forms
from .models import Ulasan, FotoUlasan

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class UlasanForm(forms.ModelForm):
    class Meta:
        model = Ulasan
        fields = ['rating', 'komentar']

class FotoUlasanForm(forms.ModelForm):
    gambar = forms.ImageField(
        widget=MultipleFileInput(attrs={'multiple': True}), 
        required=False
    )
    
    class Meta:
        model = FotoUlasan
        fields = ['gambar']

    @property
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError('Rating harus 1-5!!!!!!')
        return rating