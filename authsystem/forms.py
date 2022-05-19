from django.forms import ModelForm, PasswordInput, TextInput
from base.models import Customer, User

class UserSignInForm(ModelForm): 
    class Meta:
        model = User
        fields = ["email", "password"]
        widgets = {
            "email": TextInput(attrs={
                "class": "w-full bg-white border rounded-md shadow",
                "placeholder": "Enter your email",
            }),
            "password": PasswordInput(attrs={
                "class": "w-full bg-white border rounded-md shadow",
                "placeholder": "Password",
            })
        }

class CustomerCreationForm(ModelForm): 
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "email", "password", "phone"]
        widgets = {
            "first_name": TextInput(attrs={
                "class": "w-full bg-white border rounded-md shadow",
                "placeholder": "Firstname",
            }),
            "last_name": TextInput(attrs={
                "class": "w-full bg-white border rounded-md shadow",
                "placeholder": "Lastname",
            }),
            "phone": TextInput(attrs={
                "class": "w-full bg-white border rounded-md shadow",
                "placeholder": "Phone no.",
            }),
            "email": TextInput(attrs={
                "class": "w-full bg-white border rounded-md shadow",
                "placeholder": "Email",
            }),
            "password": PasswordInput(attrs={
                "class": "w-full bg-white border rounded-md shadow",
                "placeholder": "Password",
            })
        }