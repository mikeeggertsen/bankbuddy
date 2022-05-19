from django.forms import ChoiceField, ModelForm, TextInput
from .models import Account

class AccountCreationForm(ModelForm):
    type = ChoiceField(choices=Account.ACCOUNT_TYPES)
    class Meta:
        model = Account
        fields = ["name"]
        widgets = {
            "name": TextInput(attrs={
                "class": "",
                "placeholder": "Account name"
            }),
        }