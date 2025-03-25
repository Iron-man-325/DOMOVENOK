from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render


def index_page(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/index.html', context)


def login_page(request: WSGIRequest):
    raise NotImplementedError


def registration_page(request: WSGIRequest):
    raise NotImplementedError


from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .models import Profile, Flat, UserFlat


def profile_page(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')

    # Получение информации о профиле пользователя
    profile = Profile.objects.get(user=request.user)
    username = request.user.username
    email = request.user.email
    last_name = request.user.last_name

    # История просмотра квартир (последние 5 записей)
    viewed_flats = UserFlat.objects.filter(user=request.user).select_related('flat').order_by('-viewed_at')[:5]

    # Квартиры, добавленные пользователем
    user_flats = Flat.objects.filter(owner=request.user)

    context = {
        'email': email,
        'username': username,
        'last_name': last_name,
        'profile': profile,
        'viewed_flats': viewed_flats,
        'user_flats': user_flats,
    }
    return render(request, "HTML/profile.html", context)