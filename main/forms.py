from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, TextInput, EmailInput, PasswordInput, RadioSelect,FileInput,NumberInput
from .models import Profile, Apartment,StaticInput

User = get_user_model()


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
    name = forms.CharField(min_length=1,
                            max_length=69,
                           widget=forms.TextInput({"class": "group-input",
                                                   "placeholder": "Название"}
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
    square = forms.DecimalField(widget=forms.NumberInput({"class": "count-input",
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
    image = forms.ImageField(widget=forms.FileInput(attrs={"class": "", "onchange": "preview(this)"}))

class StaticInputForm(ModelForm):
    class Meta:
        model = StaticInput
        fields = ['water_input', 'water_receipt','water_payment','electro_payment', 'electro_receipt', 'electro_input','gas_input','gas_payment','gas_receipt','GKX_payment','GKX_receipt','rent_payment','rent_receipt']

        widgets = {
            "water_input": NumberInput(attrs={
                'class': 'desc-inp',
                'placeholder': 'Внесите расход'
            }),
            "water_payment": NumberInput(attrs={
                'class': 'desc-inp',
                'placeholder': 'Внесите плату'
            }),
            "electro_payment": NumberInput(attrs={
                'class': 'desc-inp',
                'placeholder': 'Внесите плату'
            }),
            "electro_input": NumberInput(attrs={
                'class': 'desc-inp',
                'placeholder': 'Внесите расход'
            }),
            "gas_input": NumberInput(attrs={
                'class': 'desc-inp',
                'placeholder': 'Внесите расход'
            }),
            "gas_payment": NumberInput(attrs={
                'class': 'desc-inp',
                'placeholder': 'Внесите плату'
            }),
            "GKX_payment": NumberInput(attrs={
                'class': 'desc-inp',
                'placeholder': 'Внесите плату'
            }),
            "rent_payment": NumberInput(attrs={
                'class': 'desc-inp',
                'placeholder': 'Внесите плату'
            }),
            "water_receipt": FileInput(attrs={
                'id':"water_receipt",
                'name':"photos",
                'style':"margin-top:10px;"
            }),
            "electro_receipt": FileInput(attrs={
                'id':"electro_receipt",
                'name':"photos",
                'style':"margin-top:10px;"
            }),
            "gas_receipt": FileInput(attrs={
                'id':"gas_receipt",
                'name':"photos",
                'style':"margin-top:10px;"
            }),
            "GKX_receipt": FileInput(attrs={
                'id':"GKX_receipt",
                'name':"photos",
                'style':"margin-top:10px;"
            }),
            "rent_receipt": FileInput(attrs={
                'id':"rent_receipt",
                'name':"photos",
                'style':"margin-top:10px;"
            }),
        }



# class PhotoForm(forms.ModelForm):
#     class Meta:
#         model = Photo
#         fields = "__all__"
#         widgets = {
#             "image": forms.FileInput(attrs={"class": "...", "onchange": "preview(this)"})
#         }
