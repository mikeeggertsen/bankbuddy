from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

from base.constants import MANAGER
from .models import Employee, Loan
from authsystem.utils import send_email
from django.template.loader import render_to_string

@receiver(post_save, sender=Loan, dispatch_uid="new_loan_created")
def send_new_loan_mail(sender, **kwargs):
    managers = Employee.objects.filter(role=MANAGER)
    loan = kwargs["instance"]
    for manager in managers:
        send_email(
            "BankBuddy - New loan",
            render_to_string("base/admin/new_loan_email.html", {
                "account_no": loan.account_no,
                "name": f"{manager.first_name} {manager.last_name}",
                "protocol": settings.DEFAULT_PROTOCOL,
                "domain": settings.DEFAULT_DOMAIN,
            }),
            [manager.email]
    )