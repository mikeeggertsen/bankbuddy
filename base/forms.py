from django.forms import CharField, ChoiceField, DateField, DateInput, EmailInput,  ModelChoiceField, ModelForm, NumberInput, PasswordInput, Select, TextInput, ValidationError

from base.constants import ACCOUNT_TYPES
from .models import Account, Employee, Ledger, Bank, Customer, Loan, User
from django.utils import timezone


class AccountForm(ModelForm):
    type = ChoiceField(choices=ACCOUNT_TYPES)

    def __init__(self, is_staff, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        if is_staff:
            self.fields["customer"] = ModelChoiceField(
                queryset=Customer.objects.all(), empty_label="Choose customer")
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


class TransactionForm(ModelForm):
    bank = ModelChoiceField(queryset=Bank.objects.filter(
        external=True), required=False)
    to_account = CharField()
    own_message = CharField(max_length=255)
    scheduled_date = DateField(required=False)
    debt = CharField(required=False)
    class Meta:
        model = Ledger
        fields = ["account", "amount", "message"]
        widgets = {
            "amount": NumberInput(attrs={
                "placeholder": "Amount"
            }),
            "message": TextInput(attrs={
                "placeholder": "Message to receiver"
            }),
        }

    def __init__(self, loan, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.fields['own_message'].widget.attrs['placeholder'] = 'Message to your account'
        self.fields["to_account"].widget.attrs['placeholder'] = "Account no."
        self.fields["scheduled_date"].widget = DateInput(attrs={
            "placeholder": "Scheduled date",
            "type": "date",
        })
        self.fields["account"].empty_label = "Select an account"
        self.fields["account"].required = True
        self.fields["bank"].empty_label = "Select a bank"

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'bb-input',
            })

        self.loan = loan
        if loan:
            self.fields["debt"].initial = f"${self.loan.amount}"
            self.fields["debt"].widget.attrs["readonly"] = True
            self.fields["to_account"].widget.attrs["readonly"] = True

    def clean_scheduled_date(self):
        cleaned_data = super(TransactionForm, self).clean()
        scheduled_date = cleaned_data["scheduled_date"]

        if scheduled_date and scheduled_date < timezone.now().date():
            raise ValidationError("Scheduled date must be in the future")
        return scheduled_date

    def clean(self):
        cleaned_data = super(TransactionForm, self).clean()
        account = cleaned_data["account"]
        amount = cleaned_data["amount"]
        bank = cleaned_data["bank"]
        to_account = cleaned_data["to_account"]
        if account.balance < amount:
            raise ValidationError({"account": "Account has inefficient funds"})
        if amount <= 0:
            raise ValidationError(
                {"amount": "Amount must be a greater than $0"})

        if self.loan and self.loan.amount < amount:
            raise ValidationError({"debt": "Amount must be less than total debt"})

        if bank is None:
            if self.loan and not Loan.objects.filter(account_no=to_account).exists():
                raise ValidationError(
                    "No account exists with this account no.")

            if not self.loan and not Account.objects.filter(account_no=to_account).exists():
                raise ValidationError(
                    "No account exists with this account no.")

        return cleaned_data


class ProfileForm(ModelForm):
    password = CharField(widget=PasswordInput, required=False)
    confirm_password = CharField(widget=PasswordInput, required=False)
    rank = CharField(widget=TextInput, required=False)
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "email"]

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
        self.fields["accounts"].queryset = Account.objects.filter(
            customer__id=customer_id)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'bb-input'
            })

    def clean(self):
        cleaned_data = super(LoanForm, self).clean()
        amount = cleaned_data["amount"]
        if amount <= 0:
            raise ValidationError(
                {"amount": "Amount must be a greater than $0"})
        return cleaned_data


class RankForm(ModelForm):
    class Meta:
        model = Customer
        fields = ["rank"]

    def __init__(self, *args, **kwargs):
        super(RankForm, self).__init__(*args, **kwargs)
        self.fields['rank'].widget.attrs = {'onchange': 'form.submit()'}
        self.fields['rank'].widget.attrs.update({'class': 'select-input'})


class LoanStatusForm(ModelForm):
    class Meta:
        model = Loan
        fields = ["status"]

    def __init__(self, *args, **kwargs):
        super(LoanStatusForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs = {'onchange': 'form.submit()'}
        self.fields['status'].widget.attrs.update({'class': 'select-input'})


class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = ["first_name", "last_name",
                  "phone", "email", "password", "role"]
        widgets = {
            "first_name": TextInput(attrs={
                "placeholder": "Firstname"
            }),
            "last_name": TextInput(attrs={
                "placeholder": "Lastname"
            }),
            "phone": NumberInput(attrs={
                "placeholder": "Phone"
            }),
            "email": EmailInput(attrs={
                "placeholder": "Email"
            }),
            "password": PasswordInput(attrs={
                "placeholder": "Password"
            }),
            "role": Select(),
        }

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'bb-input'
            })
