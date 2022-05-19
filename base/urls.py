from django.urls import path
from . import views

app_name = "base"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("accounts/", views.accounts, name="accounts"),
    path("accounts/new", views.create_account, name="create_account"),
    path("accounts/<int:account_no>", views.account_details, name="account"),
    path("transactions/", views.transactions, name="transactions"),
    path("profile/", views.profile, name="profile"),
]