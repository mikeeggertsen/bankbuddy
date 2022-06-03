from django.contrib import admin
from .models import Account, Customer, Employee, Ledger, Loan, ScheduledLedger, User, Bank

admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Employee)
admin.site.register(Account)
admin.site.register(Ledger)
admin.site.register(ScheduledLedger)
admin.site.register(Bank)
admin.site.register(Loan)
