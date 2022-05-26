from decimal import Decimal
from logging import exception
import os
import uuid
import requests
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from base.managers import UserManager


class Bank(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    external = models.BooleanField()

    def __str__(self):
        return f'{self.name}'


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

    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField(default=BASIC, choices=RANKS)

    class Meta:
        db_table = 'customers'


class Employee(User):
    SUPPORT = 1
    MANAGER = 2
    DEPARTMENTS = [
        (SUPPORT, 'Support'),
        (MANAGER, 'Manager'),
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
    name = models.CharField(max_length=255)
    account_no = models.IntegerField(unique=True)
    type = models.PositiveSmallIntegerField(choices=ACCOUNT_TYPES)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts'

    def __str__(self):
        return f'{self.name} - ${self.balance}'

    def save(self, *args, **kwargs):
        if self.account_no is None:
            numOfAccounts = Account.objects.all().count()
            self.account_no = settings.START_ACCOUNT_NO + numOfAccounts + 1
        super(Account, self).save(*args, **kwargs)

    @property
    def transactions(self):
        return Ledger.objects.filter(account=self.account_no)

    @property
    def balance(self):
        return self.transactions.aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)


class Ledger(models.Model):
    CREDIT = 1
    DEBIT = 2
    TRANSACTION_TYPES = [
        (CREDIT, 'Credit'),
        (DEBIT, 'Debit'),
    ]

    transaction_id = models.CharField(max_length=50)
    account = models.CharField(max_length=50)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    type = models.PositiveSmallIntegerField(choices=TRANSACTION_TYPES)
    message = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'ledger'

    def __str__(self):
        return f'{self.TRANSACTION_TYPES[self.type - 1][1]} - Account {self.account} - Amount ${self.amount}'

    @classmethod
    def make_bank_transaction(cls, credit_account, debit_account, amount, own_message, message):
        id = uuid.uuid4()
        with transaction.atomic():
            Ledger.objects.create(
                transaction_id=id,
                account=credit_account,
                amount=amount,
                type=cls.CREDIT,
                message=message,
            ).save()
            Ledger.objects.create(
                transaction_id=id,
                account=debit_account,
                amount=-amount,
                type=cls.DEBIT,
                message=own_message,
            ).save()
        return id

    @classmethod
    def make_external_transfer(cls, credit_account, debit_account, amount, own_message, message, external_bank_id):
        with transaction.atomic():
            id = uuid.uuid4()
            request_body = {
                "id": str(id),
                "senderBankId": Bank.objects.get(external=False).id,
                "receiverBankId": external_bank_id,
                "senderAccountNumber": debit_account,
                "receiverAccountNumber": credit_account,
                "amount": str(amount),
                "message": message
            }

            print("OUTGOING REQEUST BODY")
            print(request_body)

            request_headers = {
                "Token": os.environ['BANK_CONTROLLER_TOKEN'],
                "Content-Type": "application/json"
            }
            request_url = os.environ['BANK_CONTROLLER_ENDPOINT']
            response = requests.post(
                request_url, json=request_body, headers=request_headers)
            if response.status_code == 200:
                print(f"Got good response!! {response.json()}")
                Ledger.objects.create(
                    transaction_id=id,
                    account=debit_account,
                    amount=-amount,
                    type=cls.DEBIT,
                    message=own_message,
                )
            else:
                print(f"External transfer failed!! {response.json()}")

    @classmethod
    def receive_external_transfer(cls, credit_account, amount, message, transaction_id):
        print("received external transfer!!")
        with transaction.atomic():
            Ledger.objects.create(
                transaction_id=transaction_id,
                account=credit_account,
                amount=amount,
                message=message,
                type=cls.CREDIT
            )


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
