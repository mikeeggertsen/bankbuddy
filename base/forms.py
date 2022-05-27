from calendar import c
from django.forms import CharField, ChoiceField, IntegerField, ModelChoiceField, ModelForm, NumberInput, PasswordInput, TextInput, ValidationError
from .models import Account, AccountLedger, Bank, Customer, Loan, User

class AccountCreationForm(ModelForm):
    type = ChoiceField(choices=Account.ACCOUNT_TYPES)

    def __init__(self, *args, **kwargs):
        super(AccountCreationForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'bb-input'
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
    to_account = CharField()
    own_message = CharField(max_length=255)
    class Meta:
        model = AccountLedger
        fields = ["account", "amount", "message"]
        widgets = {
            "amount": NumberInput(attrs={
                "placeholder": "Amount"
            }),
            "message": TextInput(attrs={
                "placeholder": "Message to receiver"
            }),
        }

    def __init__(self, is_loan, *args, **kwargs):
        super(TransactionCreationForm, self).__init__(*args, **kwargs)
        self.fields['own_message'].widget.attrs['placeholder'] = 'Message to your account'
        self.fields["to_account"].widget.attrs['placeholder'] = "Account no."
        self.fields["account"].empty_label = "Select an account"
        self.fields["bank"].empty_label = "Select a bank"

        for field in self.fields:
            self.fields[field].widget.attrs.update({
               'class': 'bb-input',
            })
        
        self.is_loan = is_loan
        if is_loan:
            self.fields["to_account"].widget.attrs["readonly"] = True

    def clean_to_account(self):
        cleaned_data = super(TransactionCreationForm, self).clean()
        to_account = cleaned_data["to_account"]
        #TODO ADD EXTERNAL BANK ACCOUNT CHECK
        if self.is_loan and not Loan.objects.filter(account_no=to_account).exists():
            raise ValidationError("No account exists with this account no.")

        if not self.is_loan and not Account.objects.filter(account_no=to_account).exists():
            raise ValidationError("No account exists with this account no.")
        return to_account

    def clean(self):
        cleaned_data = super(TransactionCreationForm, self).clean()
        account = cleaned_data["account"]
        amount = cleaned_data["amount"]
        if account.balance < amount:
            raise ValidationError({"account": "Account has inefficient funds"})
        if amount <= 0:
            raise ValidationError({"amount": "Amount must be a greater than $0"})
        return cleaned_data

class ProfileForm(ModelForm):
    password = CharField(widget=PasswordInput,required=False)
    confirm_password = CharField(widget=PasswordInput,required=False)
    class Meta: 
        model = Customer
        fields = ["first_name", "last_name", "phone", "email", "rank"]
     
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs['placeholder'] = "Firstname"
        self.fields["last_name"].widget.attrs['placeholder'] = "Lastname"
        self.fields["phone"].widget.attrs['placeholder'] = "Phone no."
        self.fields["email"].widget.attrs['placeholder'] = "Email"
        self.fields["rank"].widget.attrs['placeholder'] = "Rank"
        self.fields["password"].widget.attrs['placeholder'] = "Password"
        self.fields["confirm_password"].widget.attrs['placeholder'] = "Confirm password"
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'bb-input',
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


class LoanForm(ModelForm):
    accounts = ModelChoiceField(queryset=None, required=True)
    class Meta:
        model = Loan
        fields = ["amount", "name"]

    def __init__(self, customer_id, *args, **kwargs):
        super(LoanForm, self).__init__(*args, **kwargs)
        self.fields["accounts"].empty_label = "Select an account"
        self.fields["amount"].widget.attrs['placeholder'] = "Amount"
        self.fields["name"].widget.attrs['placeholder'] = "Name of loan"
        self.fields["accounts"].queryset = Account.objects.filter(customer__id=customer_id)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
               'class': 'bb-input'
            })