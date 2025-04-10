from django.contrib.auth import authenticate, login
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ApartmentForm, PhotoForm
import json
from .models import Apartment


def parse(s):
    s1 = ""
    for c in s:
        if c != '[' and c != ']' and c != '"':
            s1 += c
    return s1


def add_apartment(request):
    if request.method == 'POST':
        form = ApartmentForm(request.POST, request.FILES)
        if form.is_valid():
            # Создание объекта квартиры
            apartment = Apartment.objects.create(
                number=form.cleaned_data['number'],
                housenum=form.cleaned_data['housenum'],
                stage=form.cleaned_data['stage'],
                city=form.cleaned_data['city'],
                street=form.cleaned_data['street'],
                description=form.cleaned_data['description'],
                max_people=form.cleaned_data['max_people'],
                sleeping_places=form.cleaned_data['sleeping_places'],
                sleeping_rooms=form.cleaned_data['sleeping_rooms'],
                bathrooms=form.cleaned_data['bathrooms'],
                cost_per_night=form.cleaned_data['cost_per_night'],
                prepayment=form.cleaned_data['prepayment'],
                min_nights=form.cleaned_data['min_nights'],
                free_at=form.cleaned_data['free_at'],
                image=form.cleaned_data['image']
            )
            apartment.nearby_objects = request.POST.get('nearby_objects', '')
            apartment.amenities = request.POST.get('amenities', '')
            apartment.living_rules = request.POST.get('rules', '')
            apartment.nearby_objects = parse(apartment.nearby_objects)
            apartment.amenities = parse(apartment.amenities)
            apartment.living_rules = parse(apartment.living_rules)
            apartment.save()

            return redirect('apartment_list')

    else:
        form = ApartmentForm()

    return render(request, 'pages/Flat_add.html', {'form': form})


def apartment_list(request):
    apartments = Apartment.objects.all()
    return render(request, 'pages/admin.html', {'apartments': apartments})


def index_page(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/Flat_add.html', context)


def login_view(request):
    context = {
        "error": None
    }

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('profile')
        context["error"] = "Неверное имя пользователя или пароль."

    return render(request, "pages/Login.html", context)


def show_flat(request, flat_id):
    try:
        apartment = Apartment.objects.get(id=flat_id)
        return render(request, "pages/show_flat.html", {'apartment': apartment})
    except Apartment.DoesNotExist:
        return render(request, "pages/404.html", status=404)


def login_page(request: WSGIRequest):
    raise NotImplementedError


def registration_page(request: WSGIRequest):
    raise NotImplementedError

def add_image_page(request: WSGIRequest):
    context = {
        "form": PhotoForm()
    }
    if request.method == "GET":
        return render(request, "pages/save_photo.html", context)

    form = PhotoForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
    else:
        raise NotImplementedError

    return render(request, "pages/save_photo.html", context)


