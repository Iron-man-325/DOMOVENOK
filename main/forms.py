from django import forms
from django.contrib.auth.models import User
from .models import Profile, Flat

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'last_name']

class FlatForm(forms.ModelForm):
    class Meta:
        model = Flat
        fields = ['title', 'description', 'price_per_night', 'address', 'image']