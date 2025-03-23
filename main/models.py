from django.db import models
from django.contrib.auth.models import User


class Photo(models.Model):
    image = models.ImageField(upload_to='apartment_photos/')  # Папка для хранения фото
    alt_text = models.CharField(max_length=255, blank=True, null=True, help_text="Описание изображения")

    def __str__(self):
        return f"Фото {self.id}"


class Apartment(models.Model):
    # Адрес квартиры
    city = models.CharField(max_length=69, null=True)  # Город
    street = models.CharField(max_length=69, null=True)  # Улица
    stage = models.CharField(max_length=69, null=True)  # Этаж
    number = models.CharField(max_length=69, null=True)  # номер квартиры
    housenum = models.CharField(max_length=69, null=True)  # номер дома
    # Описание квартиры
    description = models.CharField(max_length=69, blank=True)

    # Характеристики квартиры
    max_people = models.DecimalField(max_digits=10, decimal_places=2)  # Максимальное количество постояльцев
    sleeping_places = models.DecimalField(max_digits=10, decimal_places=2)  # Количество спальных мест
    sleeping_rooms = models.DecimalField(max_digits=10, decimal_places=2)  # Количество спален
    bathrooms = models.DecimalField(max_digits=10, decimal_places=2)  # Количество ванных комнат

    # Стоимость и предоплата
    cost_per_night = models.DecimalField(max_digits=10, decimal_places=2)  # Цена за ночь
    prepayment = models.DecimalField(max_digits=10, decimal_places=2)  # Предоплата

    # Минимальное количество ночей для бронирования
    min_nights = models.DecimalField(max_digits=10, decimal_places=2)

    # Дата доступности квартиры
    free_at = models.DateTimeField(blank=True, null=True)
    nearby_objects = models.TextField(default='[]')  # JSON-строка
    amenities = models.TextField(default='[]')  # JSON-строка
    living_rules = models.TextField(default='[]', blank=True)  # JSON-строка

    # Дополнительные фото
    # photos = models.ManyToManyField(Photo, related_name='additional_photos')

    def __str__(self):
        return f"{self.city}, {self.street} - {self.description[:20]}..."
