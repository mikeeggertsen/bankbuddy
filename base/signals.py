from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

from base.constants import APPROVED, CREDIT, MANAGER, REJECTED
from .models import Employee, Ledger, Loan
from authsystem.utils import send_email
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import uuid

@receiver(post_save, sender=Loan, dispatch_uid=uuid.uuid4())
def send_new_loan_mail(sender, instance, created, **kwargs):
    managers = Employee.objects.filter(role=MANAGER)
    if not created:
        for manager in managers:
            send_email(
                "BankBuddy - New loan",
                render_to_string("base/admin/new_loan_email.html", {
                    "account_no": instance.account_no,
                    "name": f"{manager.first_name} {manager.last_name}",
                    "protocol": settings.DEFAULT_PROTOCOL,
                    "domain": settings.DEFAULT_DOMAIN,
                }),
                [manager.email]
        )

    channel_layer = get_channel_layer()
    status = instance.status
    message = "Your loan has been changed to pending"
    if status == APPROVED:
        message = f"Your {instance.name} loan has been approved!"
    elif status == REJECTED:
        message = f"Your {instance.name} loan has been rejected"

    async_to_sync(channel_layer.group_send)(
        str(instance.customer.id),
        {
            'type': 'send_notification',
            'message': message,
        }
    )
    
@receiver(post_save, sender=Ledger, dispatch_uid=uuid.uuid4())
def send_transaction_toast(sender, instance, created, **kwargs):
    if instance.type == CREDIT and not created:
        channel_layer = get_channel_layer()
        message = f"You just received ${instance.amount}"
        async_to_sync(channel_layer.group_send)(
            str(instance.account.customer.id),
            {
                'type': 'send_notification',
                'message': message,
            }
        )