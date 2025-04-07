from django.contrib.auth.models import User
from django.db import models

from django.contrib.auth.models import User

class Apartment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='apartments') # имя арендодателя
    address = models.CharField(max_length=255) # адрес квартиры
    rooms = models.IntegerField() # кол - во комнат
    bathrooms = models.IntegerField() # кол - во ванных комнат
    area = models.FloatField() # удобства
    price = models.FloatField() # цена
    description = models.TextField(blank=True) # описание
    photo_links = models.TextField(blank=True) # ссылки на фото
    living_rules = models.TextField(blank=True) # правила сдачи
    available_from = models.DateField(blank=True, null=True) # колво гостей для сдачи
    beds = models.IntegerField() # кол - во кроватей
    advance_payment = models.IntegerField() #аванс
    street = models.CharField(max_length=255) # улица квартиры
    city = models.CharField(max_length=255) # город
    def __str__(self):
        return f"{self.address} - {self.rooms} комнат"

class Profile(models.Model):
    user = models.ForeignKey(User, models.CASCADE)

    def __str__(self):
        return self.user.username
