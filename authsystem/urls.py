import os
from django.urls import path, reverse_lazy

from . import views
from django.contrib.auth import views as auth_views

app_name = "authsystem"

urlpatterns = [
    path('signin/', views.sign_in, name='sign_in'),
    path('verify/', views.verify, name='verify'),
    path('resend_sms/', views.resend_sms, name='resend_sms'),
    path('signout/', views.sign_out, name='sign_out'),
    path('signup/', views.sign_up, name='sign_up'),
    path('reset_password/', auth_views.PasswordResetView.as_view(
        from_email=os.environ["FROM_EMAIL"],
        template_name="authsystem/reset_password.html",
        email_template_name="authsystem/reset_password_email.html",
        success_url=reverse_lazy("authsystem:reset_password_sent"),
    ), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(
        template_name="authsystem/reset_password_sent.html"
    ), name="reset_password_sent"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="authsystem/reset_password_form.html",
        success_url=reverse_lazy("authsystem:reset_password_complete"),
    ), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name="authsystem/reset_password_complete.html"
    ), name="reset_password_complete"),
]
