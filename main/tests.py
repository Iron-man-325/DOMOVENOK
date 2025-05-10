import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from django.utils import timezone
from django.core import mail

from .models import (
    Apartment, ExchangeRate, PaymentMethod, Profile, ViewHistory, SupportRequest,
    Account, Transaction, Rent_Apartment, StaticInput
)
from .forms import ApartmentForm, PasswordUpdateForm, StaticInputForm, UserForm, ProfileUpdateForm, UserUpdateForm


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            email='test@example.com'
        )
        Profile.objects.create(user=self.user)

    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))

    def test_registration_view(self):
        response = self.client.post(reverse('registration'), {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_profile_access_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)


class ApartmentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.profile = Profile.objects.create(user=self.user)
        self.apartment = Apartment.objects.create(
            user=self.user,
            name='Test Apartment',
            city='Test City',
            street='Test Street',
            number='1',
            housenum='1',
            max_people=2,
            sleeping_places=2,
            sleeping_rooms=1,
            bathrooms=1,
            square=50,
            cost_per_night=100,
            prepayment=50,
            min_nights=1
        )

    def test_apartment_creation(self):
        self.assertEqual(Apartment.objects.count(), 1)
        self.assertEqual(str(self.apartment), 'Test City, Test Street, 1, кв. 1')

    def test_flat_list_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_send_support_message_invalid_method(self):
        self.client.login(username='testuser', password='testpass123')
