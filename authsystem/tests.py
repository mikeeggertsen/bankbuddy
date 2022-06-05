import time
from django.test import RequestFactory, TestCase
from authsystem.models import VerificationCode
from authsystem.views import sign_in, sign_up, verify
from base.constants import BASIC
from base.models import Bank, Customer, User
from django.contrib.sessions.middleware import SessionMiddleware
class AuthTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.bank = Bank.objects.create(
            id="id_test_bank",
            name="Test Bank",
            external=False
        )
        self.user = User.objects.create_user(
            first_name="Authy",
            last_name="Junior",
            email="auth@test.dk",
            password="test",
            phone="12345",
        )

    def test_sign_in_get(self):
        request = self.factory.get("signin")
        request.user = None
        response = sign_in(request)
        self.assertEqual(response.status_code, 200)
    
    def test_sign_in_post(self):
        data = {
            "email": self.user.email,
            "password": "test",
        }
        request = self.factory.post("signin", data)
        request.user = None
        request.session = {}
        response = sign_in(request)
        self.assertEqual(response.status_code, 302)

    def test_sign_up_get(self):
        request = self.factory.get("signup")
        request.user = None
        response = sign_up(request)
        self.assertEqual(response.status_code, 200)
    
    def test_sign_up_post(self):
        data = {
            "first_name": "Steve",
            "last_name": "Wozniak",
            "email": "goat@test.dk",
            "password": "apple",
            "phone": "1234",
            "bank": self.bank.id,
        }
        request = self.factory.post("signup", data)
        request.user = None
        response = sign_up(request)
        self.assertEqual(response.status_code, 302)

    def test_verify_get(self):
        request = self.factory.get("verify")
        request.user = None
        response = verify(request)
        self.assertEqual(response.status_code, 200)
    
    def test_verify_post(self):
        code = 12345
        VerificationCode.objects.create(
            user_id=self.user.id,
            code=code
        )
        data = { "code": code }
        request = self.factory.post("verify", data)
        request.user = None
        request.session = []
        response = verify(request)
        self.assertEqual(response.status_code, 302)