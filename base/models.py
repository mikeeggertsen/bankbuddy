import email
from time import time
import uuid
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser

from base.managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(blank=False, null=False,
                             unique=True, max_length=15)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['id']
        db_table = 'users'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Customer(User):
    BASIC = 1
    SILVER = 2
    GOLD = 3
    RANKS = [
        (BASIC, 'Basic'),
        (SILVER, 'Silver'),
        (GOLD, 'Gold'),
    ]

    rank = models.PositiveSmallIntegerField(default=BASIC, choices=RANKS)

    class Meta:
        db_table = 'customers'


class Employee(User):
    SUPPORT = 1
    MODERATER = 2
    DEPARTMENTS = [
        (SUPPORT, 'Support'),
        (MODERATER, 'Moderator'),
    ]

    department = models.PositiveSmallIntegerField(choices=DEPARTMENTS)

    class Meta:
        db_table = 'employees'


class Account(models.Model):
    CHECKING = 1
    SAVINGS = 2
    SALARY = 3
    ACCOUNT_TYPES = [
        (CHECKING, 'Checking'),
        (SAVINGS, 'Savings'),
        (SALARY, 'Salary'),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='customer')
    name = models.CharField(max_length=255, default=CHECKING)
    account_no = models.IntegerField(unique=True)
    balance = models.DecimalField(decimal_places=2, max_digits=12)
    type = models.PositiveSmallIntegerField(choices=ACCOUNT_TYPES)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts'

    def __str__(self):
        return f'{self.balance}'


class Ledger(models.Model):
    CREDIT = 1
    DEBIT = 2
    TRANSACTION_TYPES = [
        (CREDIT, 'Credit'),
        (DEBIT, 'Debit'),
    ]

    transaction_id = models.CharField(max_length=50)
    to_account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='to_account')
    from_account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='from_account')
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    type = models.PositiveSmallIntegerField(choices=TRANSACTION_TYPES)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'

    @transaction
    def make_bank_transaction(self, to_acc, from_acc, transaction_amount):
        try:
            id = uuid.uuid4()
            Ledger.objects.create(
                transaction_id=id,
                to_account=to_acc,
                from_account=from_acc,
                amount=transaction_amount,
                type='Credit',
                updated_at=time.now(),
                created_at=time.now()
            )
            Ledger.objects.create(
                transaction_id=id,
                to_account=from_acc,
                from_account=to_acc,
                amount=transaction_amount,
                type='Debit',
                updated_at=time.now(),
                created_at=time.now()
            )
            return True
        except:
            return False


class Loan(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='loans',)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    balance = models.DecimalField(decimal_places=2, max_digits=12)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'loans'
