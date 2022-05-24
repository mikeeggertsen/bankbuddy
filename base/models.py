import os
from time import time
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
    name = models.CharField(max_length=255)
    account_no = models.IntegerField(unique=True)
    balance = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    type = models.PositiveSmallIntegerField(choices=ACCOUNT_TYPES)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts'

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)
        self.balance = self.check_balance()

    def __str__(self):
        return f'{self.name} - ${self.balance}'

    def save(self, *args, **kwargs):
        if self.account_no is None:
            numOfAccounts = Account.objects.all().count()
            self.account_no = settings.START_ACCOUNT_NO + numOfAccounts + 1
        super(Account, self).save(*args, **kwargs)

    def check_balance(self):
        transactions = Ledger.objects.filter(to_account=self)
        balance = 0
        for transaction in transactions:
            if transaction.type == 1:
                balance += transaction.amount
            else:
                balance -= transaction.amount
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
    message = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'ledger'

    def __str__(self):
        return f'{self.TRANSACTION_TYPES[self.type - 1][1]} - From {self.from_account} -> To {self.to_account} Amount ${self.amount}'

    @transaction.atomic
    def make_bank_transaction(
        self,
        to_acc,
        from_acc,
        transaction_amount,
        own_message,
        message,
    ):
        id = uuid.uuid4()
        credit = Ledger.objects.create(
            transaction_id=id,
            to_account=to_acc,
            from_account=from_acc,
            amount=transaction_amount,
            type=self.CREDIT,
            message=message,
        )
        debit = Ledger.objects.create(
            transaction_id=id,
            to_account=from_acc,
            from_account=to_acc,
            amount=transaction_amount,
            type=self.DEBIT,
            message=own_message,
        )
        credit.save()
        debit.save()

    @transaction.atomic
    def make_external_transfer(
        self,
        to_acc,
        from_acc,
        transaction_amount,
        own_message,
        message,
        external_bank_id
    ):
        request_body = {
            "senderBankId": Bank.objects.get(external=False).id,
            "receiverBankId": external_bank_id,
            "senderAccountNumber": from_acc.account_no,
            "receiverAccountNumber": to_acc.account_no,
            "amount": transaction_amount,
            "message": message
        }
        request_headers = {
            "Token": os.environ['BANK_CONTROLLER_TOKEN'],
            "Content-Type": "application/json"
        }
        request_url = os.environ['BANK_CONTROLLER_ENDPOINT']
        request = requests.post(
            request_url, data=request_body, headers=request_headers)
        data = request.json
        print(data)


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
