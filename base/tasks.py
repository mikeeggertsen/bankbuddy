from django.http import Http404
from django.shortcuts import get_object_or_404
from celery import shared_task
from .models import Account, Ledger, ScheduledLedger
from django.utils import timezone

@shared_task
def run_scheduled_transactions():
    now = timezone.now().date()
    scheduled_transactions = ScheduledLedger.objects.filter(scheduled_date=now)
    for record in scheduled_transactions:
        try:
            transaction_id = record.transaction_id
            account = get_object_or_404(Account, pk=record.account_id)
            type = record.type
            amount = record.amount
            if type == "2":
                amount = -record.amount
            message = record.message
            Ledger.objects.create(
                transaction_id=transaction_id,
                account=account,
                amount=amount,
                type=type,
                message=message,
            ).save()
            ScheduledLedger.objects.all().delete()
        except Http404:
            print('Failed running scheduled transaction')