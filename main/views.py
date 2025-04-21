import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect

from .forms import ApartmentForm, User, UserForm
from .models import Apartment, Profile


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


def adminn(request):
    apartments = Apartment.objects.all()
    return render(request, 'pages/admin.html', {'apartments': apartments})


def index_page(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/Flat_add.html', context)


def my_problems(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/my_problems.html', context)


def error(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/error.html', context)


def flat_list(request: WSGIRequest):
    apartments = Apartment.objects.all()
    return render(request, 'pages/flat_list_buy.html', {'apartments': apartments})


def faq_questions(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/faq_questions.html', context)


def sup(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/support_message.html', context)


def support(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/support.html', context)


def stat(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/static.html', context)


def my_flats(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/my_flats.html', context)


def redac_profile(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/redac_profile.html', context)


def profile(request: WSGIRequest):
    user = request.user
    return render(request, 'pages/profile.html', {'form': user})


def registration_page(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.data["email"],
                username=form.data["username"],
                password=form.data["password"],
                last_name=form.data["last_name"]
            )

            profile = Profile()
            profile.user = user
            profile.save()  # Фиксирует профиль в БД

            login(request, user)
            return redirect('profile')
    form = UserForm()

    data = {
        'form': form,
    }
    return render(request, "pages/regestration.html", data)


def login_page(request):
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

    return render(request, "pages/login.html", context)


@csrf_exempt
def send_support_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')

        if user_message:
            send_mail(
                'Сообщение поддержки',
                user_message,
                'no-reply@yourdomain.com',  # Письмо отправителя (например, no-reply@yourdomain.com)
                ['lebedev.egor585.lol@gmail.com'],  # Ваш электронный адрес
                fail_silently=False,
            )
            return JsonResponse({'success': True})

    return JsonResponse({'success': False})


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
