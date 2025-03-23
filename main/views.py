from django.contrib.auth import authenticate, login
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ApartmentAddForm
from .models import Apartment


def add_apartment_page(request):
    if request.method == 'POST':
        form = ApartmentAddForm(request.POST)
        if form.is_valid():
            # Создание объекта квартиры
            apartment = Apartment.objects.create(
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
                free_at=form.cleaned_data['free_at']
            )

            nearby_objects_json = request.POST.get('nearby_objects')
            if nearby_objects_json:
                apartment.nearby_objects = nearby_objects_json

            amenities_json = request.POST.get('amenities')
            if amenities_json:
                apartment.amenities = amenities_json

            rules_json = request.POST.get('rules')
            if rules_json:
                apartment.living_rules = rules_json

            apartment.save()

            return redirect('apartment_list')

    else:
        form = ApartmentAddForm()

    return render(request, 'pages/Flat_add.html', {'form': form})


def apartment_list_page(request):
    context = {'pagename': "Квартиры",
               'apartments': Apartment.objects.all()  # Да, закидывайте пользователя всеми квартирами по всей России...
               # TODO: сделать получение геопозиции пользователя и фильтрацию посылаемых ему квартир по ней
               }
    if request.GET:
        for i in list(request.GET.keys()):
            if i == "search_field":
                context['apartments'] = Apartment.objects.all()  # TODO: сделать фильтр... но по какому параметру?

    return render(request, 'pages/all_flats.html', context)


def apartment_list_admin_page(request):
    context = {'pagename': "Квартиры - Панель админа",
               'apartments': Apartment.objects.all()
               }
    return render(request, 'pages/admin.html', context)


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


def login_page(request: WSGIRequest):
    raise NotImplementedError


def registration_page(request: WSGIRequest):
    raise NotImplementedError
