from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class Account(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('RUB', 'Russian Ruble'),
        ('KZT', 'Kazakhstani Tenge'),
        # Добавьте другие валюты по необходимости
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'currency')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s {self.currency} account"

    def deposit(self, amount, description=""):
        """Пополнение счета"""
        if amount <= 0:
            raise ValueError("Amount must be positive")

        self.balance += amount
        self.save()

        Transaction.objects.create(
            account=self,
            amount=amount,
            transaction_type='deposit',
            description=description,
            status='completed'
        )
        return self.balance

    def withdraw(self, amount, description=""):
        """Снятие со счета"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if self.balance < amount:
            raise ValueError("Insufficient funds")

        self.balance -= amount
        self.save()

        Transaction.objects.create(
            account=self,
            amount=amount,
            transaction_type='withdrawal',
            description=description,
            status='completed'
        )
        return self.balance


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Пополнение'),
        ('withdrawal', 'Снятие'),
        ('transfer_in', 'Перевод (входящий)'),
        ('transfer_out', 'Перевод (исходящий)'),
        ('payment', 'Платеж'),
        ('refund', 'Возврат средств'),
    ]

    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('completed', 'Завершено'),
        ('failed', 'Ошибка'),
        ('cancelled', 'Отменено'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    reference_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account', 'created_at']),
        ]

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} for account {self.account.id}"

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)


class ExchangeRate(models.Model):
    from_currency = models.CharField(max_length=3)
    to_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=15, decimal_places=6)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('from_currency', 'to_currency')

    def __str__(self):
        return f"1 {self.from_currency} = {self.rate} {self.to_currency}"


class PaymentMethod(models.Model):
    METHOD_TYPE_CHOICES = [
        ('card', 'Банковская карта'),
        ('bank_account', 'Банковский счет'),
        ('ewallet', 'Электронный кошелек'),
        ('crypto', 'Криптовалюта'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=20, choices=METHOD_TYPE_CHOICES)
    details = models.JSONField()  # Хранение различных данных о платежных методах
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s {self.get_method_type_display()}"


class Apartment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    name=models.CharField(max_length=200,null=True)
    city = models.CharField(max_length=200, null=True)
    street = models.CharField(max_length=200, null=True)
    stage = models.CharField(max_length=200, null=True)
    number = models.CharField(max_length=200, null=True)
    housenum = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=200, blank=True)

    # Характеристики квартиры
    max_people = models.DecimalField(max_digits=10, decimal_places=0)
    sleeping_places = models.DecimalField(max_digits=10, decimal_places=0)
    sleeping_rooms = models.DecimalField(max_digits=10, decimal_places=0)
    bathrooms = models.DecimalField(max_digits=10, decimal_places=0)
    square = models.DecimalField(max_digits=10, decimal_places=0, default=1)

    cost_per_night = models.DecimalField(max_digits=10, decimal_places=0)
    prepayment = models.DecimalField(max_digits=10, decimal_places=0)

    min_nights = models.DecimalField(max_digits=10, decimal_places=0)

    free_at = models.DateTimeField(blank=True, null=True)
    nearby_objects = models.TextField(default='[]')
    amenities = models.TextField(default='[]')
    living_rules = models.TextField(default='[]', blank=True)

    image = models.ImageField(upload_to='apartment_photos/', default='default_image.jpg')  # Папка для хранения фото

    def __str__(self):
        return f"{self.city}, {self.street}, {self.housenum}, кв. {self.number}"


class Profile(models.Model):
    """
    Доп. таблица к пользователю
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username


class ViewHistory(models.Model):
    """
    История просмотра квартир
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='view_history')
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']
        unique_together = ['user', 'apartment']
        
class StaticInput(models.Model):
    apartment=models.ForeignKey(Apartment,on_delete=models.CASCADE)
    water_input= models.DecimalField(max_digits=10,decimal_places=0,blank=True, null=True)
    water_payment=models.DecimalField(max_digits=10,decimal_places=0,blank=True, null=True)
    water_receipt=models.ImageField(upload_to='apartment_photos/', default='default_image.jpg')
    electro_input= models.DecimalField(max_digits=10,decimal_places=0,blank=True, null=True)
    electro_payment=models.DecimalField(max_digits=10,decimal_places=0,blank=True, null=True)
    electro_receipt=models.ImageField(upload_to='apartment_photos/', default='default_image.jpg')
    gas_input= models.DecimalField(max_digits=10,decimal_places=0,blank=True, null=True)
    gas_payment=models.DecimalField(max_digits=10,decimal_places=0,blank=True, null=True)
    gas_receipt= models.ImageField(upload_to='apartment_photos/', default='default_image.jpg')
    rent_payment= models.DecimalField(max_digits=10,decimal_places=0,blank=True, null=True)
    rent_receipt=models.ImageField(upload_to='apartment_photos/', default='default_image.jpg')
    GKX_payment= models.DecimalField(max_digits=10,decimal_places=0,blank=True, null=True)
    GKX_receipt=models.ImageField(upload_to='apartment_photos/', default='default_image.jpg')
    submitted_at = models.DateTimeField(auto_now_add=True)

class Rent_Apartment(models.Model):
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='landlord_rentals')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_rentals')
    price = models.IntegerField(default=0)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    dates = models.IntegerField(default=0)
    status=models.CharField(max_length=100)


class SupportRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_requests')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # Для хранения до 3 файлов
    photo1 = models.ImageField(upload_to='support_photos/', null=True, blank=True)
    photo2 = models.ImageField(upload_to='support_photos/', null=True, blank=True)
    photo3 = models.ImageField(upload_to='support_photos/', null=True, blank=True)

    def photos(self):
        return [p for p in [self.photo1, self.photo2, self.photo3] if p]