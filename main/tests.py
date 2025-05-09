import json
from django.test import TestCase, Client, RequestFactory
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
            name="Test Apartment",
            city="Test City",
            street="Test Street",
            number="1",
            housenum="1",
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
        self.assertEqual(str(self.apartment), "Test City, Test Street, 1, кв. 1")

    def test_flat_list_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_send_support_message_invalid_method(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('send_support_message'))

    def test_send_support_message_empty_message(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('send_support_message'), {
            'message': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], False)

    def test_full_user_flow(self):
        # Регистрация
        response = self.client.post(reverse('registration'), {
            'username': 'newtestuser',
            'password': 'newtestpass123',
            'email': 'newtest@example.com',
            'first_name': 'NewTest',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 302)
        
        # Логин
        self.client.login(username='newtestuser', password='newtestpass123')
        
        # Добавление квартиры
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('add_apartment'), {
            'number': '3',
            'housenum': '3',
            'stage': '1',
            'city': 'Test City',
            'street': 'Test Street',
            'max_people': 3,
            'sleeping_places': 3,
            'sleeping_rooms': 2,
            'bathrooms': 1,
            'square': 60,
            'cost_per_night': 120,
            'prepayment': 60,
            'min_nights': 2,
            'name': 'Test Apartment 3',
            'image': image,
            'nearby_objects': '[]',
            'amenities': '[]',
            'rules': '[]'
        })
        self.assertEqual(response.status_code, 302)
        
        # Проверка списка квартир
        response = self.client.get(reverse('my_flats'))
        self.assertEqual(len(response.context['apartments']), 1)
        
        # Выход
        response = self.client.post(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))

class RentApartmentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
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
        self.rent = Rent_Apartment.objects.create(
            landlord=self.user,
            tenant=self.user,
            apartment=self.apartment,
            price=100,
            dates=1,
            status='active'
        )

    def test_rent_apartment_creation(self):
        self.assertEqual(self.rent.price, 100)
        self.assertEqual(self.rent.status, 'active')
        self.assertEqual(self.rent.landlord, self.user)

class ViewHistoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
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
        self.view_history = ViewHistory.objects.create(
            user=self.user,
            apartment=self.apartment
        )

    def test_view_history_creation(self):
        self.assertEqual(self.view_history.user, self.user)
        self.assertEqual(self.view_history.apartment, self.apartment)

class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.profile = Profile.objects.create(user=self.user)

    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, 'testuser')

class ApartmentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
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
        self.assertEqual(self.apartment.name, 'Test Apartment')
        self.assertEqual(self.apartment.city, 'Test City')
        self.assertEqual(self.apartment.max_people, 2)

class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.account = Account.objects.create(user=self.user, currency='USD', balance=100)

    def test_transaction_creation(self):
        transaction = Transaction.objects.create(
            account=self.account,
            amount=50,
            transaction_type='deposit',
            status='completed'
        )
        self.assertEqual(transaction.amount, 50)
        self.assertEqual(transaction.transaction_type, 'deposit')

class AccountModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.account = Account.objects.create(user=self.user, currency='USD', balance=100)

    def test_account_creation(self):
        self.assertEqual(self.account.balance, 100)
        self.assertEqual(self.account.currency, 'USD')
        self.assertTrue(self.account.is_active)

    def test_deposit(self):
        self.account.deposit(50)
        self.assertEqual(self.account.balance, 150)
        self.assertEqual(Transaction.objects.count(), 1)

    def test_withdraw(self):
        self.account.withdraw(50)
        self.assertEqual(self.account.balance, 50)
        self.assertEqual(Transaction.objects.count(), 1)

    def test_send_support_message_no_message(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('send_support_message'), {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], False)

    def test_account_withdraw_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(200)
    
    def test_account_deposit_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.account.deposit(-50)

    def test_transaction_status_update(self):
        transaction = Transaction.objects.create(
            account=self.account,
            amount=50,
            transaction_type='deposit',
            status='pending'
        )
        transaction.status = 'completed'
        transaction.save()
        self.assertIsNotNone(transaction.completed_at)

    def test_exchange_rate_creation(self):
        exchange_rate = ExchangeRate.objects.create(
            from_currency='USD',
            to_currency='EUR',
            rate=0.85
        )
        self.assertEqual(str(exchange_rate), "1 USD = 0.85 EUR")

    def test_payment_method_creation(self):
        payment_method = PaymentMethod.objects.create(
            user=self.user,
            method_type='card',
            details={'card_number': '4242424242424242'},
            is_default=True
        )
        self.assertEqual(payment_method.get_method_type_display(), 'Банковская карта')

    def test_static_input_creation(self):
        def test_support_request_str_method(self):
            self.assertTrue(str(self.support_request).startswith("testuser: Test message"))
            
class FormsTestCase(TestCase):
    def setUp(self):
        self.image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")

    def test_apartment_form_valid(self):
        form = ApartmentForm(data={
            'number': '2',
            'housenum': '2',
            'stage': '1',
            'city': 'Test City',
            'street': 'Test Street',
            'description': 'Test',
            'max_people': 2,
            'sleeping_places': 2,
            'sleeping_rooms': 1,
            'bathrooms': 1,
            'cost_per_night': 100,
            'prepayment': 50,
            'min_nights': 1,
            'square': 50,
            'name': 'Test Apartment'
        }, files={'image': self.image})

    def test_apartment_form_invalid(self):
        form = ApartmentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertGreater(len(form.errors), 5)

    def test_user_form_valid(self):
        form = UserForm(data={
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertTrue(form.is_valid())

    def test_profile_update_form_valid(self):
        form = ProfileUpdateForm(data={}, files={'avatar': self.image})

    def test_user_update_form_valid(self):
        form = UserUpdateForm(data={
            'first_name': 'New',
            'last_name': 'Name',
            'email': 'new@example.com'
        })
        self.assertTrue(form.is_valid())

    def test_password_update_form_mismatch(self):
        form = PasswordUpdateForm(data={
            'old_password': 'oldpass',
            'new_password': 'newpass123',
            'confirm': 'differentpass'
        })

class SignalsTest(TestCase):
    def test_admin_page_access_denied_for_non_staff(self):
        self.client.login(username='testuser', password='testpass123')