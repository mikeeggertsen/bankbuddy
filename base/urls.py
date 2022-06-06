from django.urls import path
from . import views

app_name = "base"

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("customers/", views.customers, name="customers"),
    path("customers/<int:id>", views.customer_details, name="customer"),
    path("customers/new", views.create_customer, name="create_customer"),
    path("accounts/", views.accounts, name="accounts"),
    path("accounts/new", views.create_account, name="create_account"),
    path("accounts/<int:account_no>", views.account_details, name="account"),
    path("transfer/", views.create_transaction, name="transfer"),
    path("loans/", views.loans, name="loans"),
    path("loans/<int:account_no>", views.loan_details, name="loan"),
    path("loans/apply", views.apply_loan, name="apply_loan"),
    path("loans/<int:account_no>/payment", views.loan_payment, name="loan_payment"),
    path("employees/", views.employees, name="employees"),
    path("employees/new", views.create_employee, name="create_employee"),
    path("employees/<int:id>", views.employee_details, name="create_employee"),
    path("profile/", views.profile, name="profile"),
    path("transfer-request/", views.transfer_request, name="transfer_request")
]
