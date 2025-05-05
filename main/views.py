from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .forms import ApartmentForm, UserForm, PasswordUpdateForm, ProfileUpdateForm, UserUpdateForm
from .models import Apartment, Profile, User, ViewHistory


def get_base_context(pagename: str = "", **kwargs):
    """
    Функция для получения базового словаря ``context`` для всех шаблонов.
    Внутри него к ключу ``menu`` привязан список имён ссылок в меню,
    поэтому **строго не рекомендуется** использовать ключ ``menu``.

    Пример 1::

        context = get_base_context("Главная", menu=[])  # В меню пропадут ссылки

    Пример 2::

        context = get_base_context("Главная", form=SomeForm())
        # context['form'] = SomeForm()

    :param str pagename: Название страницы, помещаемое в <title>
    :param kwargs: Можно добавлять необходимые пары ключ-значение, просто передавая в параметры пары ключ=значение
    """

    class MenuUrlContext:
        def __init__(self, url_name: str, name: str):
            self.url_name = url_name
            self.name = name

    context = {'pagename': pagename,
               'menu': [MenuUrlContext('index', 'Главная'),
                        MenuUrlContext('stat', 'Статистика'),
                        MenuUrlContext('index', 'Чаты'),
                        MenuUrlContext('faq', 'Q&A'),
                        MenuUrlContext('support', 'Поддержка'),
                        MenuUrlContext('redact', 'Настройки'),
                        ]
               }
    for key in kwargs.keys():
        context[key] = kwargs[key]

    return context


def parse(s):
    s1 = ""
    for c in s:
        if c != '[' and c != ']' and c != '"':
            s1 += c
    return s1


def index_page(request: WSGIRequest):
    return flat_list(request)


@login_required
def add_apartment(request):
    context = get_base_context('Добавление квартиры')
    form = ApartmentForm()
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
                image=form.cleaned_data['image'],
                square=form.cleaned_data['square'],
                name=form.cleaned_data['name'],
                user=request.user
            )
            apartment.nearby_objects = request.POST.get('nearby_objects', '')
            apartment.amenities = request.POST.get('amenities', '')
            apartment.living_rules = request.POST.get('rules', '')
            apartment.nearby_objects = parse(apartment.nearby_objects)
            apartment.amenities = parse(apartment.amenities)
            apartment.living_rules = parse(apartment.living_rules)

            apartment.save()

            return redirect('apartment_list')

    context['form'] = form

    return render(request, 'pages/Flat_add.html', context)


@login_required
def adminn(request):
    apartments = Apartment.objects.all()
    context = get_base_context('Квартиры - панель админа', apartments=apartments)
    return render(request, 'pages/admin.html', context)


@login_required
def show_flat(request, flat_id):
    try:
        apartment = Apartment.objects.get(id=flat_id)
        context = get_base_context(str(apartment), apartment=apartment)
        ViewHistory.objects.create(user=request.user, apartment=apartment)
        return render(request, "pages/show_flat.html", {'apartment': apartment})
    except Apartment.DoesNotExist:
        return render(request, "pages/404.html", status=404)


@login_required
def my_problems(request: WSGIRequest):
    context = get_base_context('Мои проблемы')
    return render(request, 'pages/my_problems.html', context)


def error(request: WSGIRequest):
    context = get_base_context('Error')
    return render(request, 'pages/error.html', context)


def flat_list(request: WSGIRequest):
    context = get_base_context('Квартиры', apartments=Apartment.objects.all())
    return render(request, 'pages/flat_list_buy.html', context)


def faq_questions(request: WSGIRequest):
    class Question:
        def __init__(self, q: str, a: str = ""):
            self.q = q
            self.a = a

    questions = [Question("Как выставить объявление об аренде квартиры?",
                          "Кнопка справа сверху, в меню, \"Разместить объявление\". Авторизация обязательна."),
                 Question("Как оплатить квартиру?",
                          "Вы можете оплатить квартиру прямо на сайте с помощью своего виртуального кошелька."),
                 Question("Как увидеть статистику по заработку?",
                          "Никак, мы - не приложение вашего банка."),
                 Question("Как добавить квитанции об оплате?",
                          "Никак."),
                 Question("Можно ли связаться с администрацией сайта?",
                          "Нет. Зачем связываться с администраторами, когда есть поддержка?"),
                 Question("Присутствует ли на сайте поверка квартир перед выкладкой?",
                          "Нет, модератор просто галочки тыкает с перерывом на сон."),
                 Question("?",
                          "Ещё вопросы? На нашем сайте есть поддержка..."),
                 ]

    context = get_base_context('Часто задаваемые вопросы', questions=questions)

    return render(request, 'pages/faq_questions.html', context)


@login_required
def sup(request: WSGIRequest):
    context = get_base_context('Поддержка')
    return render(request, 'pages/support_message.html', context)


@login_required
def support(request: WSGIRequest):
    context = get_base_context('Поддержка')
    return render(request, 'pages/support.html', context)


@login_required
def stat(request: WSGIRequest):
    context = get_base_context('Статистика')
    return render(request, 'pages/static.html', context)


@login_required
def my_flats(request: WSGIRequest):
    apartments = Apartment.objects.filter(user=request.user)
    context = get_base_context('Ваши квартиры', apartments=apartments)

    return render(request, 'pages/my_flats.html', context)


@login_required
def redact_profile(request: WSGIRequest):
    usr = User.objects.get_by_natural_key(request.user)
    prof = Profile.objects.get(user=usr)
    change_profile_form = ProfileUpdateForm()
    change_user_form = UserUpdateForm()
    change_password_form = PasswordUpdateForm()
    if request.method == "POST":
        change_profile_form = ProfileUpdateForm(request.POST, request.FILES)
        if change_profile_form.is_valid():
            if change_profile_form.cleaned_data['avatar']:
                prof.avatar = change_profile_form.cleaned_data['avatar']
                prof.save()

        change_user_form = UserUpdateForm(request.POST)
        if change_user_form.is_valid():
            data = change_user_form.cleaned_data
            usr.first_name = data['first_name']
            usr.last_name = data['last_name']
            usr.email = data['email']
            usr.save()

        change_password_form = PasswordUpdateForm(request.POST)
        if change_password_form.is_valid():
            data = change_password_form.cleaned_data
            check_user = authenticate(request, username=request.user, password=data['old_password'])
            if check_user != User.objects.get_by_natural_key(request.user):
                messages.add_message(request, messages.ERROR,
                                     "Неверный старый пароль (или пользователь недействителен)")
            elif data['new_password'] != data['confirm']:
                messages.add_message(request, messages.ERROR,
                                     "Поля \"Новый пароль\" и \"Подтвердите новый пароль\" не совпадают")
            else:
                usr.set_password(data['new_password'])
                usr.save()
                login(request, usr)
                messages.add_message(request, messages.SUCCESS,
                                     "Ваш пароль изменён")

    context = get_base_context(
        'Редактирование профиля',
        profile=prof,
        username=usr.username,
        email=usr.email,
        last_name=usr.last_name,
        change_profile_form=change_profile_form,
        change_user_form=change_user_form,
        change_password_form=change_password_form
    )

    return render(request, 'pages/redact_profile.html', context)


@login_required
def profile_page(request: WSGIRequest):
    if request.method == 'POST':
        logout(request)
        return redirect('login')

    user = User.objects.get_by_natural_key(request.user)
    profile = Profile.objects.get(user=user)
    history = ViewHistory.objects.filter(user=user).select_related('apartment')
    apartments = Apartment.objects.all()
    user_flats = Apartment.objects.filter(user=user)
    context = get_base_context(
        'Профиль',
        user=user,
        profile=profile,
        history=history,
        apartments=apartments,
        myflats=user_flats
    )
    return render(request, 'pages/profile.html', context)


def registration_page(request):
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.data["username"],
                password=form.data["password"],
                email=form.data["email"],
                first_name=form.data["first_name"],
                last_name=form.data["last_name"]
            )

            profile = Profile()
            profile.user = user
            profile.save()  # Фиксирует профиль в БД

            login(request, user)
            return redirect('profile')
        if User.objects.filter(username=form.data["username"]):
            messages.add_message(request, messages.ERROR, "Пользователь с таким ником уже существует")

    context = get_base_context('Регистрация', form=form)
    return render(request, "registration/registration.html", context)


def login_page(request):
    context = get_base_context('Авторизация', error=None)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if 'next' in request.GET.keys():
                return redirect(request.GET.get('next'))
            return redirect('profile')
        context["error"] = "Неверное имя пользователя или пароль."

    return render(request, "registration/login.html", context)


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
                ['pavel1234111@gmail.com'],
            )
            for f in files[:3]:
                email.attach(f.name, f.read(), f.content_type)
            email.send(fail_silently=False)
            return JsonResponse({'success': True})

    return JsonResponse({'success': False})
