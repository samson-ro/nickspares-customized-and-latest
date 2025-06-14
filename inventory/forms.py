from django import forms
from .models import SparePart, Supplier, PartCategory

class SparePartForm(forms.ModelForm):
    class Meta:
        model = SparePart
        fields = ['name', 'part_number', 'category', 'quantity', 'price', 'supplier', 'procurement_cost']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'part_number': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'procurement_cost' : forms.TextInput(attrs={'class': 'form-control'})
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PartCategoryForm(forms.ModelForm):
    class Meta:
        model = PartCategory
        fields = ['name']