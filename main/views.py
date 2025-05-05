import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from .forms import ApartmentForm, User, UserForm
from .models import Apartment, Profile
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect

from .forms import ApartmentForm, User, UserForm,StaticInputForm
from .models import Apartment, Profile,ViewHistory,Rent_Apartment,StaticInput

def get_base_context(pagename: str = "", **kwargs):
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
                        MenuUrlContext('redact_profile', 'Настройки'),
                        ]
               }
    for key, value in kwargs:
        context[key] = value

    return context

def parse(s):
    s1 = ""
    for c in s:
        if c != '[' and c != ']' and c != '"':
            s1 += c
    return s1


import json
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage

@login_required
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
                image=form.cleaned_data['image'],
                square=form.cleaned_data['square'],
                name=form.cleaned_data['name'],
                user = request.user
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

@login_required
def adminn(request):
    apartments = Apartment.objects.all()
    return render(request, 'pages/admin.html', {'apartments': apartments})

@login_required
def index_page(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/Flat_add.html', context)

@login_required
def my_problems(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/my_problems.html', context)

@login_required
def error(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/error.html', context)

@login_required
def flat_list(request: WSGIRequest):
    apartments = Apartment.objects.all()
    return render(request, 'pages/flat_list_buy.html', {'apartments': apartments})



@login_required
def sup(request: WSGIRequest):
    rent=Rent_Apartment.objects.filter(tenant=request.user,status='active')
    if not rent:
        return HttpResponse("У вас нет активной аренды", status=400)
    
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
                )
            stat.save()
    else:
        form = StaticInputForm()
    context={
        'form':form
    }
    return render(request, 'pages/support_message.html', context)

@login_required
def support(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/support.html', context)

@login_required
def stat(request, flat_id):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/static.html', context)

@login_required
def my_flats(request: WSGIRequest):
    apartments = Apartment.objects.filter(user=request.user)
    context = {
        'pagename': "Главная",
        'apartments': apartments
    }
    return render(request, 'pages/my_flats.html', context)

@login_required
def redac_profile(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/redac_profile.html', context)

@login_required
def profile(request: WSGIRequest):
    user = request.user
    history = ViewHistory.objects.filter(user=request.user).select_related('apartment')
    apartments = Apartment.objects.all()
    my_flats = Apartment.objects.filter(user=request.user)
    context={
        'form': user,
        'history':history,
        'apartments':apartments,
        'myflats':my_flats
    }
    return render(request, 'pages/profile.html', context)


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


@csrf_exempt
@login_required
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

    return render(request, "pages/login.html", context)

@login_required
def show_flat(request, flat_id):
    try:
        apartment = Apartment.objects.get(id=flat_id)
        ViewHistory.objects.update_or_create(user=request.user, apartment=apartment)
        return render(request, "pages/show_flat.html", {'apartment': apartment})
    except Apartment.DoesNotExist:
        return render(request, "pages/404.html", status=404)
    
@login_required   
def faq_questions(request: WSGIRequest):
    class Question:
        def __init__(self, q: str, a: str = ""):
            self.q = q
            self.a = a

    context = get_base_context('Часто задаваемые вопросы')
    context['questions'] = [Question("Как выставить квартиру на продажу?",
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

    return render(request, 'pages/faq_questions.html', context)
