from datetime import timedelta
from django.utils import timezone
import random
from django.db import models
from authsystem.api import send_sms
from django.conf import settings
class VerificationCode(models.Model):
    user_id = models.IntegerField()
    code = models.CharField(unique=True, max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'verification_codes'

    def save(self, *args, **kwargs):
        expires_at=timezone.now() + timedelta(minutes=15)
        self.expires_at = expires_at
        super(VerificationCode, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.code} - created at {self.created_at}'

    @classmethod
    def verify(cls, code):
        token = cls.objects.filter(code=code).get()
        if token.expires_at < timezone.now():
            raise Exception("Verification code has expired, re-send sms to try again")
        if token:
            token.delete()
            return token.user_id
        return None

    @classmethod
    def send_code(cls, user):
        code = 0
        while True:
            code = random.randrange(10000, 99999)
            if not cls.objects.filter(code=code).exists():
                cls.objects.create(user_id=user.pk, code=code)
                if settings.DEBUG:
                    print('Verification Code', code)
                    break
                else:
                    message = f"BankBuddy: Your verification code is: {code}. Please don't reply"
                    send_sms(message, user.phone)
                    break
