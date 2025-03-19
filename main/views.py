from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ApartmentForm
from .models import Apartment

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

def login_page(request: WSGIRequest):
    raise NotImplementedError


def registration_page(request: WSGIRequest):
    raise NotImplementedError