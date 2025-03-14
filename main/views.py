from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ApartmentForm
from .models import Apartment
def add_apartment(request):
    if request.method == 'POST':
        form = ApartmentForm(request.POST)
        if form.is_valid():
            # Создание объекта квартиры
            apartment = Apartment.objects.create(
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
                free_at=form.cleaned_data['free_at']
            )

            nearby_objects_json = request.POST.get('nearby_objects')
            if nearby_objects_json:
                apartment.nearby_objects = nearby_objects_json


            amenities_json = request.POST.get('amenities')
            if amenities_json:
                apartment.amenities = amenities_json


            rules_json = request.POST.get('rules')
            if rules_json:
                apartment.living_rules = rules_json

            apartment.save()

            return redirect('apartment_list')

    else:
        form = ApartmentForm()

    return render(request, 'pages/Flat_add.html', {'form': form})

def apartment_list(request):
    apartments = Apartment.objects.all()
    return render(request, 'pages/admin.html', {'apartments': apartments})
def index_page(request: WSGIRequest):
    context = {
        'pagename': "Главная"
    }
    return render(request, 'pages/Flat_add.html', context)


def login_page(request: WSGIRequest):
    raise NotImplementedError


def registration_page(request: WSGIRequest):
    raise NotImplementedError