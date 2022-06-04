from django.forms import EmailField, Form, CharField, ModelForm, PasswordInput, TextInput
from base.models import Customer

class SignInForm(Form): 
    email = EmailField(widget=TextInput(attrs={'placeholder': 'Email'}))
    password = CharField(widget=PasswordInput(attrs={"placeholder": "Password"}))

    def __init__(self, *args, **kwargs):
        super(SignInForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({ 'class': 'bb-input' })

class SignUpForm(ModelForm): 
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
        self.fields["code"].widget.attrs.update({ 'class': 'bb-input' })
