from django.forms import ModelForm, PasswordInput, TextInput
from base.models import Customer, User

class UserSignInForm(ModelForm): 

    def __init__(self, *args, **kwargs):
        super(UserSignInForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'border-0 rounded w-full bg-white shadow'
            })
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

    def __init__(self, *args, **kwargs):
        super(CustomerCreationForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'border-0 rounded w-full bg-white shadow'
            })
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