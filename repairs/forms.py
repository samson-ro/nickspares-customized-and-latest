from django import forms
from django.forms import inlineformset_factory

from inventory.models import SparePart
from .models import RepairRecord, RepairPart, MotorcycleModel, Motorcycle

from employees.models import Employee

class RepairRecordForm(forms.ModelForm):
    class Meta:
        model = RepairRecord
        fields = '__all__'
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'mechanic': forms.Select(attrs={'class': 'form-control'}),
            'motorcycle_model': forms.TextInput(attrs={'class': 'form-control'}),
            'complaint': forms.TextInput(attrs={'class': 'form-control'}),
            'work_done': forms.TextInput(attrs={'class': 'form-control'}),
            'cost_of_service': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'date_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class RepairPartForm(forms.ModelForm):
    class Meta:
        model = RepairPart
        fields = ['part', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['part'].queryset = SparePart.objects.all() # Ensure parts dropdown includes all parts

RepairPartFormSet = inlineformset_factory(
    RepairRecord,
    RepairPart,
    form=RepairPartForm,
    extra=3,  
    can_delete=False
)

class MotorcycleModelForm(forms.ModelForm):
    class Meta:
        model = MotorcycleModel
        fields = ['name', 'manufacturer']

class MotorcycleForm(forms.ModelForm):
    class Meta:
        model = Motorcycle
        fields = ['model', 'license_plate', 'year', 'customer']

class RepairReportForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    mechanic = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        required=False,
        empty_label="All Mechanics"
    )