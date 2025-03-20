from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, TextInput, EmailInput, PasswordInput, RadioSelect
from .models import Profile

User = get_user_model()

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'last_name', 'email', 'password']

        widgets={
            "username":TextInput(attrs={
                'class': 'enter-field-create',
                'placeholder':'Ваше имя'
            }),
            "email": EmailInput(attrs={
                'class': 'enter-field-create',
                'placeholder': 'Почта'
            }),
            "password": PasswordInput(attrs={
                'class': 'enter-field-create',
                'placeholder': 'Пароль'
            }),
            "last_name": TextInput(attrs={
                'class': 'enter-field-create',
                'placeholder': 'Фамилия'
            }),
        }

