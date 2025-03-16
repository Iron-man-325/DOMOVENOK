from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import Profile
from .forms import UserForm, User, SettingsForm


def index_page(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/index.html', context)


def login_page(request: WSGIRequest):
    raise NotImplementedError


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

            profile = Profile()  # Создание объекта профиля (в ОЗУ)
            profile.user = user
            profile.save()  # Фиксирует профиль в БД

            login(request, user)
            return redirect('profile')
    form = UserForm()

    data = {
        'form': form,
    }
    return render(request, "HTML/creating-ak.html", data)

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

    return render(request, "registration/login.html", context)
