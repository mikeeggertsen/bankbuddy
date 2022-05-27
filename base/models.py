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

class BaseAccount(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    account_no = models.IntegerField(unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True

class Account(BaseAccount):
    CHECKING = 1
    SAVINGS = 2
    SALARY = 3
    ACCOUNT_TYPES = [
        (CHECKING, 'Checking'),
        (SAVINGS, 'Savings'),
        (SALARY, 'Salary'),
    ]

    type = models.PositiveSmallIntegerField(choices=ACCOUNT_TYPES)
    class Meta:
        db_table = 'accounts'

    def save(self, *args, **kwargs):
        if self.account_no is None:
            numOfAccounts = Account.objects.all().count()
            numOfLoans = Loan.objects.all().count()
            self.account_no = settings.START_ACCOUNT_NO + numOfAccounts + numOfLoans + 1
        super(Account, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}: ${self.balance}'
        
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

    @property
    def balance(self):
        return self.transactions.aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)

    @property
    def transactions(self):
        return Ledger.objects.filter(account=self).order_by("-created_at")

class Loan(BaseAccount):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3
    STATUS_TYPES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected')
    ]

    amount = models.IntegerField()
    status = models.PositiveSmallIntegerField(choices=STATUS_TYPES, default=PENDING)

    class Meta:
        db_table = 'loans'

    def save(self, *args, **kwargs):
        if self.account_no is None:
            numOfAccounts = Account.objects.all().count()
            numOfLoans = Loan.objects.all().count()
            self.account_no = settings.START_ACCOUNT_NO + numOfAccounts + numOfLoans + 1
        super(Loan, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}: ${self.total_debt}'

    @classmethod
    def make_bank_transaction(cls, credit_account, debit_account, amount, own_message, message):
        id = uuid.uuid4()
        with transaction.atomic():
            Ledger.objects.create(
                transaction_id=id,
                loan=credit_account,
                amount=amount,
                type=1,
                message=message,
            ).save()
            Ledger.objects.create(
                transaction_id=id,
                account=debit_account,
                amount=-amount,
                type=2,
                message=own_message,
            ).save()
        return id

    @property
    def total_paid(self):
        return self.transactions.aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)
    
    @property
    def total_debt(self):
       return self.amount - self.total_paid

    @property
    def percent_finish(self):
        return self.total_paid / self.amount * 100

    @property
    def transactions(self):
        return Ledger.objects.filter(loan=self)

class Ledger(models.Model):
    CREDIT = 1
    DEBIT = 2
    TRANSACTION_TYPES = [
        (CREDIT, 'Credit'),
        (DEBIT, 'Debit'),
    ]

    transaction_id = models.CharField(max_length=50)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    type = models.PositiveSmallIntegerField(choices=TRANSACTION_TYPES)
    message = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def make_external_transfer(cls, credit_account, debit_account, amount, own_message, message, external_bank_id):
        with transaction.atomic():
            id = uuid.uuid4()
            request_body = {
                "id": str(id),
                "senderBankId": Bank.objects.get(external=False).id,
                "receiverBankId": external_bank_id,
                "senderAccountNumber": debit_account.account_no,
                "receiverAccountNumber": credit_account,
                "amount": str(amount),
                "message": message
            }

            request_headers = {
                "Token": os.environ['BANK_CONTROLLER_TOKEN'],
                "Content-Type": "application/json"
            }
            request_url = os.environ['BANK_CONTROLLER_ENDPOINT']
            response = requests.post(
                request_url, json=request_body, headers=request_headers)
            if response.status_code == 200:
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
        with transaction.atomic():
            Ledger.objects.create(
                transaction_id=transaction_id,
                account=credit_account,
                amount=amount,
                message=message,
                type=cls.CREDIT
            )
