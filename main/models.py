from django.db import models


class Profile(models.Model):
    """
    Доп. таблица к пользователю
    """
    pass

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    """Профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

class Flat(models.Model):
    """Модель квартиры"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255)
    image = models.ImageField(upload_to='flats/', null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class UserFlat(models.Model):
    """История просмотра квартир"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)