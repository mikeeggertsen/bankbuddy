from django.urls import path
from . import views

app_name = "base"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("accounts/", views.accounts, name="accounts"),
    path("transactions/", views.transactions, name="transactions"),
    path("profile/", views.profile, name="profile"),
]