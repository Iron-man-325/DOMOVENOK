from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from .forms import ApartmentForm, User, UserForm
from .models import Apartment, Profile
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage


def add_apartment(request):
    if request.method == 'POST':
        form = ApartmentForm(request.POST)
        if form.is_valid():
            form.request = request
            form.save()
            return redirect('apartments_list')
    else:
        form = ApartmentForm()
    return render(request, 'pages/Flat_add.html', {'form': form})


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
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/flat_list_buy.html', context)


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
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/profile.html', context)


def registration_page(request):
    if request.method == 'POST':
        form = UserForm()
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
        user_message = request.POST.get('message', '')
        files = request.FILES.getlist('photos')

        if user_message:
            email = EmailMessage(
                'Сообщение поддержки',
                user_message,
                'no-reply@yourdomain.com',
                ['lebedev.egor585.lol@gmail.com'],
            )
            for f in files[:3]:
                email.attach(f.name, f.read(), f.content_type)
            email.send(fail_silently=False)
            return JsonResponse({'success': True})

    return JsonResponse({'success': False})
