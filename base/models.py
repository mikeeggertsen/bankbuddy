import email
from time import time
import uuid
from webbrowser import get
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
        return f'{self.customer} - {self.name} - {self.balance}'

    def check_balance(self):
        transactions = Ledger.objects.filter(to_account=self)
        balance = 0
        for transaction in transactions:
            balance += transaction.amount
        return balance


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
    message = models.CharField(max_length=100)

    class Meta:
        db_table = 'ledger'

    def __str__(self):
        return f'${self.transaction_id}: ${self.type} from {self.from_account}, to {self.to_account}, amount {self.amount}'

    @transaction.atomic
    def make_bank_transaction(self, to_acc, from_acc, transaction_amount, own_message, receiver_message):
        if from_acc.check_balance() >= transaction_amount:
            try:
                id = uuid.uuid4()
                Ledger.objects.create(
                    transaction_id=id,
                    to_account=to_acc,
                    from_account=from_acc,
                    amount=transaction_amount,
                    type='Credit',
                    updated_at=time.now(),
                    created_at=time.now(),
                    message=receiver_message
                )
                Ledger.objects.create(
                    transaction_id=id,
                    to_account=from_acc,
                    from_account=to_acc,
                    amount=-transaction_amount,
                    type='Debit',
                    updated_at=time.now(),
                    created_at=time.now(),
                    message=own_message
                )
                return True
            except:
                return False
        print(
            f'Failed to make transaction from: {from_acc.account_no} to: {to_acc.account_no} due to insuffiecient funds.')
        return False


class Loan(models.Model):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3
    STATUS_TYPES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected')
    ]

    status = models.PositiveSmallIntegerField(
        choices=STATUS_TYPES, default=PENDING)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='loans',)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    balance = models.DecimalField(decimal_places=2, max_digits=12)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'loans'
