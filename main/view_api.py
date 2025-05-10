from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

import json

from main.models import Apartment, User
from django.core.exceptions import ValidationError


def check_request_apartment(data: dict):
    """
    Проверяет необходимые поля, для создания апартаментов (см. файл models.py).
    Измените поля, если они отличаются с моделью
    """

    required_fields = [
        'user_id', 'max_people', 'sleeping_places',
        'sleeping_rooms', 'bathrooms', 'cost_per_night',
        'prepayment', 'min_nights'
    ]

    for field in required_fields:
        if field not in data:
            return JsonResponse(
                {'error': f'Missing required field: {field}'},
                status=400
            )

    try:
        user = User.objects.get(pk=data['user_id'])
    except Exception:
        return JsonResponse(
            {'error': 'User not found'},
            status=404
        )


@require_http_methods(["POST"])
def create_apartment(request: WSGIRequest):
    data = json.loads(request.body)
    error = check_request_apartment(data)
    if error:
        return error

    user = User.objects.get(pk=data['user_id'])

    apartment = Apartment(
        user=user,
        name=data.get('name'),
        city=data.get('city'),
        street=data.get('street'),
        stage=data.get('stage'),
        number=data.get('number'),
        housenum=data.get('housenum'),
        description=data.get('description', ''),

        max_people=data['max_people'],
        sleeping_places=data['sleeping_places'],
        sleeping_rooms=data['sleeping_rooms'],
        bathrooms=data['bathrooms'],
        square=data.get('square', 1),

        cost_per_night=data['cost_per_night'],
        prepayment=data['prepayment'],
        min_nights=data['min_nights'],

        free_at=data.get('free_at'),
        nearby_objects=data.get('nearby_objects', '[]'),
        amenities=data.get('amenities', '[]'),
        living_rules=data.get('living_rules', '[]')
        # картинку не передать через JSON
    )

    apartment.full_clean()
    apartment.save()

    return JsonResponse(
        {'id': apartment.id, 'message': f'Запись создана: {apartment}'},
        status=201
    )
