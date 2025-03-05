from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render


def index_page(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/Flat_add.html', context)


def login_page(request: WSGIRequest):
    raise NotImplementedError


def registration_page(request: WSGIRequest):
    raise NotImplementedError
