from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ApartmentForm
from .models import Apartment
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

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
def flat_list(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/flat_list_buy.html', context)
def sup(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/support_message.html', context)
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
def login_page(request: WSGIRequest):
    raise NotImplementedError


def registration_page(request: WSGIRequest):
    raise NotImplementedError


@csrf_exempt
def send_support_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')

        if user_message:
            send_mail(
                'Сообщение поддержки',  # Тема письма
                user_message,  # Тело письма
                'no-reply@yourdomain.com',  # Письмо отправителя (например, no-reply@yourdomain.com)
                ['lebedev.egor585.lol@gmail.com'],  # Ваш электронный адрес
                fail_silently=False,
            )
            return JsonResponse({'success': True})

    return JsonResponse({'success': False})