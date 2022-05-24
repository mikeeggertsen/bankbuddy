from django.forms import Form, CharField, EmailField, ModelForm, PasswordInput, TextInput, ValidationError
from base.models import Customer, User

class UserSignInForm(Form): 
    email = EmailField(widget=TextInput(attrs={'placeholder': 'Email'}))
    password = CharField(widget=PasswordInput(attrs={"placeholder": "Password"}))

    def __init__(self, *args, **kwargs):
            super(UserSignInForm, self).__init__(*args, **kwargs)

            for field in self.fields:
                self.fields[field].widget.attrs.update({
                    'class': 'border-0 rounded w-full bg-white shadow'
                })

class CustomerCreationForm(ModelForm): 
    def __init__(self, *args, **kwargs):
        super(CustomerCreationForm, self).__init__(*args, **kwargs)
        self.fields["bank"].empty_label = "Select a bank"

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'border-0 rounded w-full bg-white shadow'
            })
    class Meta:
        model = Customer
        fields = ["bank", "first_name", "last_name", "email", "password", "phone"]
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