from django.forms import CharField, ChoiceField, IntegerField, ModelChoiceField, ModelForm, NumberInput, TextInput
from .models import Account, Bank, Ledger

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
    bank = ModelChoiceField(queryset=Bank.objects.all())
    to_account = IntegerField()
    own_message = CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        super(TransactionCreationForm, self).__init__(*args, **kwargs)
        self.fields['own_message'].widget.attrs['placeholder'] = 'Message to your account'
        self.fields["from_account"].empty_label = "Select an account"
        self.fields["bank"].empty_label = "Select a bank"

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'border-0 rounded w-full bg-white shadow'
            })

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