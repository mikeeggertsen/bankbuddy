from django.urls import path
from . import views

app_name = "authsystem"

urlpatterns = [
   path('signin/', views.sign_in, name='sign_in'),
   path('signout/', views.sign_out, name='sign_out'),
   path('signup/', views.sign_up, name='sign_up'),
   path('password_reset/', views.password_reset, name='password_reset'),
]