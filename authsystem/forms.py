from django.forms import Form, CharField, EmailField, ModelForm, PasswordInput, TextInput, ValidationError
from base.models import Customer

class SignInForm(Form): 
    email = EmailField(widget=TextInput(attrs={'placeholder': 'Email'}))
    password = CharField(widget=PasswordInput(attrs={"placeholder": "Password"}))

    def __init__(self, *args, **kwargs):
            super(SignInForm, self).__init__(*args, **kwargs)

            for field in self.fields:
                self.fields[field].widget.attrs.update({
                    'class': 'bb-input'
                })

class SignUpForm(ModelForm): 
    first_name = CharField(widget=TextInput(attrs={"placeholder": "Firstname"}), required=True)
    last_name = CharField(widget=TextInput(attrs={"placeholder": "Lastname"}), required=True)
    class Meta:
        model = Customer
        fields = ["bank", "first_name", "last_name", "email", "password", "phone"]
        widgets = {
            "first_name": TextInput(attrs={
                "placeholder": "Firstname",
            }),
            "last_name": TextInput(attrs={
                "placeholder": "Lastname",
            }),
            "phone": TextInput(attrs={
                "placeholder": "Phone no.",
            }),
            "email": TextInput(attrs={
                "placeholder": "Email",
            }),
            "password": PasswordInput(attrs={
                "placeholder": "Password",
            })
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields["bank"].empty_label = "Select a bank"

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'bb-input'
            })

class VerifyForm(Form):
    code = CharField(widget=TextInput(attrs={"placeholder": "Verification code"}), max_length=5)

    def __init__(self, *args, **kwargs):
        super(VerifyForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'border-0 rounded w-full bg-white shadow'
            })