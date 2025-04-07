from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, TextInput, EmailInput, PasswordInput, RadioSelect
from .models import Profile,Apartment
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

class ApartmentForm(forms.ModelForm):
    city = forms.CharField(max_length=255, label='Город')
    street = forms.CharField(max_length=255, label='Улица')
    description = forms.CharField(widget=forms.Textarea, label='Описание', required=False)
    beds = forms.IntegerField(label='Количество спальных мест')
    rooms = forms.IntegerField(label='Спальни')
    bathrooms = forms.IntegerField(label='Ванны')
    price_per_night = forms.FloatField(label='Стоимость за одну ночь')
    advance_payment = forms.FloatField(label='Аванс')
    min_rental_days = forms.IntegerField(label='Минимальный срок аренды')
    available_from = forms.DateField(label='Свободно с', required=False)
    living_rules = forms.CharField(widget=forms.Textarea, label='Правила проживания', required=False)
    photo_links = forms.CharField(widget=forms.Textarea, label='Ссылки на фотографии', required=False)

    class Meta:
        model = Apartment
        fields = ('address', 'area', 'price')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].label = 'Адрес'
        self.fields['address'].widget.attrs.update({
            'class': 'group-input',
            'placeholder': 'Адрес'
        })

        self.fields['city'].widget.attrs.update({
            'class': 'group-input',
            'placeholder': 'Город'
        })
        self.fields['street'].widget.attrs.update({
            'class': 'group-input',
            'placeholder': 'Улица'
        })
        self.fields['description'].widget.attrs.update({
            'class': 'description',
            'placeholder': 'Описание'
        })
        self.fields['beds'].widget.attrs.update({
            'class': 'count-input',
            'placeholder': 'Количество спальных мест'
        })
        self.fields['rooms'].widget.attrs.update({
            'class': 'count-input',
            'placeholder': 'Спальни'
        })
        self.fields['bathrooms'].widget.attrs.update({
            'class': 'count-input',
            'placeholder': 'Ванны'
        })
        self.fields['price_per_night'].widget.attrs.update({
            'class': 'group-input',
            'placeholder': 'Стоимость за одну ночь'
        })
        self.fields['advance_payment'].widget.attrs.update({
            'class': 'group-input',
            'placeholder': 'Аванс'
        })
        self.fields['min_rental_days'].widget.attrs.update({
            'class': 'count-input',
            'placeholder': 'Минимальный срок аренды'
        })
        self.fields['available_from'].widget.attrs.update({
            'class': 'count-input',
            'placeholder': 'Свободно с',
            'type': 'date'
        })
        self.fields['living_rules'].widget.attrs.update({
            'class': 'description',
            'placeholder': 'Правила проживания'
        })
        self.fields['photo_links'].widget.attrs.update({
            'class': 'description',
            'placeholder': 'Ссылки на фотографии'
        })

    def save(self, commit=True):
        apartment = super().save(commit=False)
        apartment.user = self.request.user
        apartment.address = self.cleaned_data['address']
        apartment.city = self.cleaned_data['city']
        apartment.street = self.cleaned_data['street']
        apartment.description = self.cleaned_data['description']
        apartment.beds = self.cleaned_data['beds']
        apartment.rooms = self.cleaned_data['rooms']
        apartment.bathrooms = self.cleaned_data['bathrooms']
        apartment.price = self.cleaned_data['price_per_night']
        apartment.living_rules = self.cleaned_data['living_rules']
        apartment.photo_links = self.cleaned_data['photo_links']
        apartment.available_from = self.cleaned_data['available_from']

        if commit:
            apartment.save()
        return apartment