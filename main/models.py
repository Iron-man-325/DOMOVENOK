from django.db import models
from django.contrib.auth.models import User
import json

class Apartment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='apartments')
    address = models.CharField(max_length=255)
    rooms = models.IntegerField()
    bathrooms = models.IntegerField()
    amenities = models.TextField(default='[]', blank=True)  # Удобства
    price = models.FloatField()
    description = models.TextField(blank=True)
    photo_links = models.TextField(blank=True)
    living_rules = models.TextField(default='[]', blank=True)  # Правила
    available_from = models.DateField(blank=True, null=True)
    beds = models.IntegerField()
    advance_payment = models.IntegerField()
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.address} - {self.rooms} комнат"

