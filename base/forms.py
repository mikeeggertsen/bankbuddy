from django.forms import CharField, ChoiceField, IntegerField, ModelChoiceField, ModelForm, NumberInput, PasswordInput, TextInput, ValidationError
from .models import Account, Bank, Customer, Ledger, User

class AccountCreationForm(ModelForm):
    type = ChoiceField(choices=Account.ACCOUNT_TYPES)

    def __init__(self, *args, **kwargs):
        super(AccountCreationForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'border-0 rounded w-full bg-white shadow'
            })
    class Meta:
        model = Account
        fields = ["name"]
        widgets = {
            "name": TextInput(attrs={
                "class": "",
                "placeholder": "Account name"
            }),
        }

class TransactionCreationForm(ModelForm):
    bank = ModelChoiceField(queryset=Bank.objects.all(), required=False)
    to_account = IntegerField()
    own_message = CharField(max_length=255)
    class Meta:
        model = Ledger
        fields = ["from_account", "amount", "message"]
        widgets = {
            "to_account": NumberInput(attrs={
                "placeholder": "Account no."
            }),
            "amount": NumberInput(attrs={
                "placeholder": "Amount"
            }),
            "message": TextInput(attrs={
                "placeholder": "Message to receiver"
            }),
        }

    def __init__(self, *args, **kwargs):
        super(TransactionCreationForm, self).__init__(*args, **kwargs)
        self.fields['own_message'].widget.attrs['placeholder'] = 'Message to your account'
        self.fields["from_account"].empty_label = "Select an account"
        self.fields["bank"].empty_label = "Select a bank"

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'border-0 rounded w-full bg-white shadow'
            })

    def clean_to_account(self):
        cleaned_data = super(TransactionCreationForm, self).clean()
        to_account = cleaned_data["to_account"]
        #TODO ADD EXTERNAL BANK ACCOUNT CHECK
        if Account.objects.filter(account_no=to_account).none:
            raise ValidationError("No account exists with this account no.")
        return to_account

    def clean(self):
        cleaned_data = super(TransactionCreationForm, self).clean()
        from_acc = cleaned_data["from_account"]
        amount = cleaned_data["amount"]
        balance = from_acc.check_balance()
        if balance < amount:
            raise ValidationError({"from_account": "Account has inefficient funds"})
        return cleaned_data

class ProfileForm(ModelForm):
    password = CharField(widget=PasswordInput,required=False)
    confirm_password = CharField(widget=PasswordInput,required=False)
    class Meta: 
        model = Customer
        fields = ["first_name", "last_name", "phone", "email", "rank"]
        widgets = {
            "email": TextInput(attrs={
                "hidden": True
            }),
            "rank": TextInput(attrs={
                "hidden": True
            })
        }
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'border-0 rounded w-full bg-white shadow'
            })

    def clean_email(self):
        cleaned_data = super(ProfileForm, self).clean()
        email = cleaned_data["email"]
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("User with this email already exists") 
        return email

    def clean_phone(self):
        cleaned_data = super(ProfileForm, self).clean()
        phone = cleaned_data["phone"]
        if User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise ValidationError("User with this phone no. already exists") 
        return phone

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        password = cleaned_data["password"]
        confirm_password = cleaned_data["confirm_password"]
        if password != confirm_password:
            raise ValidationError({"password": "Password must match"}) 
        return cleaned_data
