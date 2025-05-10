import uuid
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import EmailMessage, send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .forms import (ApartmentForm, PasswordUpdateForm, ProfileUpdateForm, 
                   StaticInputForm, UserForm, UserUpdateForm)
from .models import (Apartment, Profile, Rent_Apartment, StaticInput,
                    SupportRequest, User, ViewHistory)


def get_base_context(pagename: str = "", **kwargs):
    """
    Функция для получения базового словаря context для всех шаблонов.
    Внутри него к ключу menu привязан список имён ссылок в меню.
    """
    class MenuUrlContext:
        def __init__(self, url_name: str, name: str):
            self.url_name = url_name
            self.name = name

    context = {
        'pagename': pagename,
        'menu': [
            MenuUrlContext('index', 'Главная'),
            MenuUrlContext('my_flats', 'Мои Квартиры'),
            MenuUrlContext('profile', 'Профиль'),
            MenuUrlContext('faq', 'Q&A'),
            MenuUrlContext('support', 'Поддержка'),
            MenuUrlContext('redact', 'Настройки'),
            MenuUrlContext('sup', 'Внеение данных'),
        ]
    }
    context.update(kwargs)
    return context


def parse(s):
    """Удаляет из строки символы [, ] и \"."""
    return ''.join(c for c in s if c not in ('[', ']', '"'))


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
                user=request.user,
                key = uuid.uuid4().hex[:10]
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
def admin_view(request):
    apartments = Apartment.objects.all()
    context = get_base_context('Квартиры - панель админа', apartments=apartments)
    return render(request, 'pages/admin.html', context)


@login_required
def show_flat(request, flat_id):
    apartment = get_object_or_404(Apartment, id=flat_id)
    ViewHistory.objects.update_or_create(
        user=request.user, 
        apartment=apartment,
        price=1
    )
    context = get_base_context(str(apartment), apartment=apartment)
    return render(request, "pages/show_flat.html", context)


@login_required
def my_problems(request: WSGIRequest):
    context = get_base_context('Мои проблемы')
    return render(request, 'pages/my_problems.html', context)


def error_page(request: WSGIRequest):
    context = get_base_context('Error')
    return render(request, 'pages/error.html', context)


def flat_list(request: WSGIRequest):
    apartments = Apartment.objects.filter(status="available")
    context = get_base_context('Главная', apartments=apartments)
    return render(request, 'pages/flat_list_buy.html', context)


@login_required
def support_message(request: WSGIRequest):
    rent = Rent_Apartment.objects.filter(
        tenant=request.user, 
        status='active'
    ).first()
    
    if not rent:
        return HttpResponse("У вас нет активной аренды", status=400)

    if request.method == 'POST':
        form = StaticInputForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('support')
    
    context = get_base_context('Поддержка', form=StaticInputForm())
    return render(request, 'pages/support_message.html', context)


@login_required
def  support(request: WSGIRequest):
    requests = SupportRequest.objects.filter(user=request.user).order_by('-created_at')
    context = get_base_context('Поддержка', requests=requests)
    return render(request, 'pages/support.html', context)


@login_required
def stat(request: WSGIRequest, flat_id):
    apartment = get_object_or_404(Apartment, id=flat_id)
    rents = Rent_Apartment.objects.filter(apartment=apartment)
    stats = StaticInput.objects.filter(apartment=flat_id)
    cash = sum(rent.price * rent.dates for rent in rents) if rents.exists() else 0

    context = get_base_context(
        'Мои квартиры',
        apartment=apartment,
        cash=cash,
        rents=rents,
        stat=stats
    )
    return render(request, 'pages/static.html', context)


@login_required
def my_flats(request: WSGIRequest):
    apartments = Apartment.objects.filter(user=request.user)
    cash = sum(
        elem.price * elem.dates 
        for apartment in apartments 
        for elem in Rent_Apartment.objects.filter(apartment=apartment)
    )
    
    context = get_base_context('Мои квартиры', apartments=apartments, cash=cash)
    return render(request, 'pages/my_flats.html', context)


@login_required
def redact_profile(request: WSGIRequest):
    user = request.user
    prof = Profile.objects.get(user=user)
    
    if request.method == "POST":
        profile_form = ProfileUpdateForm(request.POST, request.FILES)
        user_form = UserUpdateForm(request.POST)
        password_form = PasswordUpdateForm(request.POST)
        
        if profile_form.is_valid() and profile_form.cleaned_data['avatar']:
            prof.avatar = profile_form.cleaned_data['avatar']
            prof.save()

        if user_form.is_valid():
            user_form.save()
            
        if password_form.is_valid():
            data = password_form.cleaned_data
            if not user.check_password(data['old_password']):
                messages.error(request, "Неверный старый пароль")
            elif data['new_password'] != data['confirm']:
                messages.error(request, "Пароли не совпадают")
            else:
                user.set_password(data['new_password'])
                user.save()
                login(request, user)
                messages.success(request, "Пароль успешно изменён")
    else:
        profile_form = ProfileUpdateForm()
        user_form = UserUpdateForm(instance=user)
        password_form = PasswordUpdateForm()

    context = get_base_context(
        'Редактирование профиля',
        profile=prof,
        username=user.username,
        email=user.email,
        last_name=user.last_name,
        change_profile_form=profile_form,
        change_user_form=user_form,
        change_password_form=password_form
    )
    return render(request, 'pages/redact_profile.html', context)


@login_required
def profile_page(request: WSGIRequest):
    user = request.user
    profile = Profile.objects.get(user=user)
    history = ViewHistory.objects.filter(user=user).select_related('apartment')
    user_flats = Apartment.objects.filter(user=user)
    
    context = get_base_context(
        'Профиль',
        user=user,
        profile=profile,
        history=history,
        apartments=Apartment.objects.all(),
        myflats=user_flats
    )
    return render(request, 'pages/profile.html', context)


def registration_page(request):
    form = UserForm()
    
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('profile')
        if User.objects.filter(username=form.data["username"]).exists():
            messages.error(request, "Пользователь с таким ником уже существует")

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
            support_request = SupportRequest.objects.create(
                user=request.user,
                message=user_message,
            )
            email = EmailMessage(
                'Сообщение поддержки',
                user_message,
                'no-reply@yourdomain.com',
                ['pavel1234111@gmail.com'],
            )
            for idx, f in enumerate(files[:3]):
                setattr(support_request, f'photo{idx + 1}', f)
                email.attach(f.name, f.read(), f.content_type)
            support_request.save()
            email.send(fail_silently=False)
            return JsonResponse({'success': True})

    return JsonResponse({'success': False})


@login_required
def my_support_requests(request):
    requests = SupportRequest.objects.filter(user=request.user).order_by('-created_at')
    context = get_base_context('Мои запросы', requests=requests)
    return render(request, 'pages/my_support_requests.html', context)


@login_required   
def faq_questions(request: WSGIRequest):
    class Question:
        def __init__(self, q: str, a: str = ""):
            self.q = q
            self.a = a

    questions = [Question("Как выставить квартиру на продажу?",
                                     "Никак."),
                Question("Как оплатить квартиру?",
                            "Вы можете оплатить квартиру прямо на сайте с помощью T Pay."),
                Question("Как увидеть статистику по заработку?",
                            "Никак, мы - не приложение вашего банка."),
                Question("Как добавить квитанции об оплате?",
                            "Никак."),
                Question("Можно ли связаться с администрацией сайта?",
                            "Нет, идите к чёрту, проект сдан, мы сваливаем в закат."),
                Question("Присутствует ли на сайте поверка квартир перед выкладкой?",
                            "Нет, модератор просто галочки тыкает с перерывом на сон."
                            + " Ваша заявка не модерируется?"
                            + " Ничего не можем поделать, модератору здоровье важнее этой заявки."),
                Question("?",
                            "?"),
                ]
    
    context = get_base_context('Часто задаваемые вопросы', questions=questions)
    return render(request, 'pages/faq_questions.html', context)


def update_apartment_status(request, apartment_id):
    if request.method == 'POST':
        apartment = get_object_or_404(Apartment, id=apartment_id)
        if request.user == apartment.user:
            apartment.status = request.POST.get('status')
            apartment.save()
    return redirect('stat', flat_id=apartment_id)


def rent_apartment(request, flat_id, dates):
    apartment = get_object_or_404(Apartment, id=flat_id)
    Rent_Apartment.objects.create(
        tenant=request.user,
        landlord=apartment.user,
        price=apartment.cost_per_night,
        dates=dates,
        apartment=apartment,
        status='active'
    )
    apartment.status = 'rented'
    apartment.save()
    return redirect('flat_detail', flat_id=flat_id)


@login_required
def contact_owner(request, flat_id):
    apartment = get_object_or_404(Apartment, id=flat_id)
    send_mail(
        f'Запрос по квартире #{flat_id} от {request.user.username}',
        f'''Пользователь хочет связаться:
        Имя: {request.user.username}
        Email: {request.user.email}
        ID квартиры: {flat_id}''',
        settings.DEFAULT_FROM_EMAIL,
        [apartment.user.email],  
        fail_silently=False,
    )
    return redirect('flat_detail', flat_id=flat_id)


def logout_page(request):
    logout(request)
    return redirect('login')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
import json
from .models import Apartment

@csrf_exempt
def search_apartments(request):
    if request.method == 'POST':
        try:
            # Для Django < 3.1 используйте request.POST
            data = request.POST
            
            city = data.get('city', '').strip()
            street = data.get('street', '').strip()
            
            if not city:
                return JsonResponse({
                    'success': False,
                    'message': 'Город обязателен для поиска'
                }, status=400)
            
            apartments = Apartment.objects.filter(city__icontains=city)
            
            if street:
                apartments = apartments.filter(street__icontains=street)
            
            apartments_list = []
            for apt in apartments:
                apartments_list.append({
                    'id': apt.id,
                    'name': apt.name,
                    'city': apt.city,
                    'street': apt.street,
                    'cost_per_night': str(apt.cost_per_night),
                    'image': apt.image.url if apt.image else ''
                })
            
            return JsonResponse({
                'success': True,
                'apartments': apartments_list
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Ошибка сервера: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Неверный метод запроса'
    }, status=405)
def sup(request: WSGIRequest):
    rent=Rent_Apartment.objects.filter(tenant=request.user,status='active')
    rent=Rent_Apartment.objects.filter(tenant=request.user,status='active').first()
    if not rent:
        return redirect('error')
    
    if request.method == 'POST':
        form=StaticInputForm(request.POST, request.FILES)
        if form.is_valid():
            stat=StaticInput.objects.create(
                apartment=rent.apartment,
                water_input=form.cleaned_data['water_input'],
                water_payment=form.cleaned_data['water_payment'],
                water_receipt=form.cleaned_data['water_receipt'],
                electro_input=form.cleaned_data['electro_input'],
                electro_payment=form.cleaned_data['electro_payment'],
                electro_receipt=form.cleaned_data['electro_receipt'],
                gas_input=form.cleaned_data['gas_input'],
                gas_payment=form.cleaned_data['gas_payment'],
                gas_receipt=form.cleaned_data['gas_receipt'],
                GKX_payment=form.cleaned_data['GKX_payment'],
                GKX_receipt=form.cleaned_data['GKX_receipt'],
                rent_payment=form.cleaned_data['rent_payment'],
                rent_receipt=form.cleaned_data['rent_receipt'], 
                submitted_at=timezone.now()
                )
            stat.save()
        else:
            print('ERrror Valid')
    else:
        form = StaticInputForm()
        print(form.errors)
        print(form.is_valid())
    context=get_base_context('Внесение данных',
        form=form
    )
    return render(request, 'pages/support_message.html', context)
