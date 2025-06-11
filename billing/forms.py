from django import forms
from .models import Invoice, PurchasedPart
from inventory.models import SparePart
from django.forms import modelformset_factory

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 
                  'repair', 
                  'paid', ''
                  'payment_method']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'repair': forms.Select(attrs={'class': 'form-control'}),
            'paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }

class PurchasedPartForm(forms.ModelForm):
    class Meta:
        model = PurchasedPart
        fields = ['part', 
                  'quantity']


PurchasedPartFormSet = modelformset_factory(
    PurchasedPart,
    form=PurchasedPartForm,
    extra=2,  #inventory selection, can be increased or reduced 
    can_delete=True
)
