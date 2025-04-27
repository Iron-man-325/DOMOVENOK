from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, TextInput, EmailInput, PasswordInput, RadioSelect

from .models import Apartment, Profile


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'last_name', 'email', 'password']

        widgets = {
            "username": TextInput(attrs={
                'class': 'enter-field-create',
                'placeholder': 'Ваше имя'
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


class ApartmentForm(forms.Form):
    housenum = forms.CharField(min_length=1,
                               max_length=69,
                               widget=forms.TextInput({"class": "group-input",
                                                       "placeholder": "Номер дома"}
                                                      )
                               )
    stage = forms.CharField(min_length=1,
                            max_length=69,
                            widget=forms.TextInput({"class": "group-input",
                                                    "placeholder": "Этаж"}
                                                   )
                            )
    number = forms.CharField(min_length=1,
                             max_length=69,
                             widget=forms.TextInput({"class": "group-input",
                                                     "placeholder": "Номер квартиры"}
                                                    )
                             )
    city = forms.CharField(min_length=1,
                           max_length=69,
                           widget=forms.TextInput({"class": "group-input",
                                                   "placeholder": "Город"}
                                                  )
                           )
    street = forms.CharField(min_length=1,
                             max_length=69,
                             widget=forms.TextInput({"class": "group-input",
                                                     "placeholder": "Улица"}
                                                    )
                             )

    description = forms.CharField(min_length=1,
                                  max_length=69,
                                  widget=forms.TextInput({"class": "description"})
                                  )

    max_people = forms.DecimalField(widget=forms.NumberInput({"class": "count-input",
                                                              "placeholder":
                                                                  "Укажите максимальное количество постояльцев"
                                                              }
                                                             )
                                    )
    sleeping_places = forms.DecimalField(widget=forms.NumberInput({"class": "count-input",
                                                                   "placeholder": "Укажите количество спальных мест"}
                                                                  )
                                         )
    sleeping_rooms = forms.DecimalField(widget=forms.NumberInput({"class": "count-input",
                                                                  "placeholder": "Укажите число спален"}
                                                                 )
                                        )
    bathrooms = forms.DecimalField(widget=forms.NumberInput({"class": "count-input",
                                                             "placeholder": "Укажите число ванных"}
                                                            )
                                   )

    cost_per_night = forms.DecimalField(widget=forms.NumberInput({"class": "group-input",
                                                                  "placeholder": "₽0"}
                                                                 )
                                        )
    prepayment = forms.DecimalField(widget=forms.NumberInput({"class": "group-input",
                                                              "placeholder": "₽0"}
                                                             )
                                    )
    min_nights = forms.DecimalField(widget=forms.NumberInput({"class": "count-input",
                                                              "placeholder": "Количество ночей"}
                                                             )
                                    )
    free_at = forms.DateTimeField(widget=forms.DateTimeInput({"class": "count-input",
                                                              "placeholder": "Добавить даты"}
                                                             )
                                  )
    image = forms.ImageField(widget=forms.FileInput(attrs={"class": "...", "onchange": "preview(this)"}))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'last_name']
