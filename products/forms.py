from django import forms
from accounts.models import Order

class BankTransferForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment_proof', 'transaction_note',]
        widgets = {
            'transaction_note': forms.Textarea(attrs={'rows': 3}),
        }
