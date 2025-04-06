from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ApartmentForm
from .models import Apartment
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def get_base_context(pagename: str = ""):
    class MenuUrlContext:
        def __init__(self, url_name: str, name: str):
            self.url_name = url_name
            self.name = name
    return {'pagename': pagename,
            'menu': [MenuUrlContext('index', 'Главная'),
                     MenuUrlContext('stat', 'Статистика'),
                     MenuUrlContext('index', 'Чаты'),
                     MenuUrlContext('faq', 'Q&A'),
                     MenuUrlContext('support', 'Поддержка'),
                     MenuUrlContext('redact_profile', 'Настройки'),
                     ]
            }


def index_page(request: WSGIRequest):
    return flat_list(request)


def add_apartment(request):
    context = get_base_context('Добавление квартиры')
    if request.method == 'POST':
        form = ApartmentForm(request.POST)
        if not form.is_valid():
            context['form'] = form
            return render(request, 'pages/Flat_add.html', context)
        form.request = request
        form.save()
        return redirect('flat-list')
    else:
        context['form'] = ApartmentForm()
    return render(request, 'pages/Flat_add.html', context)


def flat_list(request: WSGIRequest):
    context = get_base_context('Квартиры')
    return render(request, 'pages/flat_list_buy.html', context)


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


def sup(request: WSGIRequest):
    context = get_base_context('Поддержка')
    return render(request, 'pages/support_message.html', context)


def stat(request: WSGIRequest):
    context = get_base_context('Статистика')
    return render(request, 'pages/static.html', context)


def my_flats(request: WSGIRequest):
    context = get_base_context('Ваши квартиры')
    return render(request, 'pages/my_flats.html', context)


def redact_profile(request: WSGIRequest):
    context = get_base_context('Редактирование профиля')
    return render(request, 'pages/redact_profile.html', context)


def profile(request: WSGIRequest):
    context = get_base_context('Профиль')
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
