from django.shortcuts import render, get_object_or_404, redirect
from .models import RepairRecord, RepairPart, MotorcycleModel, Motorcycle
from .forms import RepairPartFormSet, RepairRecordForm, RepairPartForm, MotorcycleModelForm, MotorcycleForm, RepairReportForm
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.template.loader import get_template
from django.http import HttpResponse
import weasyprint
from django.utils.timezone import make_aware

from weasyprint import HTML
from django.template.loader import render_to_string
import tempfile

# List all repair records
@login_required
def repair_list(request):
    pending_repairs = RepairRecord.objects.filter(status='Pending')
    completed_repairs = RepairRecord.objects.filter(status='Completed')
    cancelled_repairs = RepairRecord.objects.filter(status='Cancelled')
    
    context = {
        'pending_repairs': pending_repairs,
        'completed_repairs': completed_repairs,
        'cancelled_repairs': cancelled_repairs,
    }
    return render(request, 'repairs/repair_list.html', context)

# Show a single repair record and its parts
@login_required
def repair_detail(request, pk):
    repair = get_object_or_404(RepairRecord, pk=pk)
    parts = RepairPart.objects.filter(repair=repair)
    return render(request, 
                 'repairs/repair_detail.html',
                 {'repair': repair, 'parts': parts})

@login_required
def add_repair(request):
    if request.method == 'POST':
        form = RepairRecordForm(request.POST)
        formset = RepairPartFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            repair = form.save(commit=False)     

            if form.cleaned_data['status'] == 'Completed':
                for part_form in formset:

                    if part_form.cleaned_data and not part_form.cleaned_data.get('DELETE'):
                        part = part_form.cleaned_data['part']
                        quantity = part_form.cleaned_data['quantity']

                        if part.quantity < quantity:
                            part_form.add_error('quantity', f"Only {part.quantity} in stock for '{part.name}'.")

                            return render(request, 'repairs/repair_form.html', {
                                'form': form,
                                'formset': formset,
                                'title': 'Add Repair'
                            })           
            repair.save()
            parts = formset.save(commit=False)
            for part in parts:
                part.repair = repair
                part.save()
                if repair.status == 'Completed':
                    part.part.quantity -= part.quantity
                    part.part.save()    

            return redirect('repair_list')
    else:
        form = RepairRecordForm()
        formset = RepairPartFormSet()
        
    return render(request, 'repairs/repair_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Add Repair'
    })


@login_required
def edit_repair(request, pk):
    repair = get_object_or_404(RepairRecord, pk=pk)
    old_status = repair.status  # Capture the original status BEFORE processing the form
    RepairPartFormSet = inlineformset_factory(
        RepairRecord,
        RepairPart,
        form=RepairPartForm,
        extra=2,
        can_delete=True
    )

    if request.method == 'POST':
        repair_form = RepairRecordForm(request.POST, instance=repair)
        formset = RepairPartFormSet(request.POST, instance=repair)

        if repair_form.is_valid() and formset.is_valid():
            # First validate stock if changing to Completed
            new_status = repair_form.cleaned_data['status']
            if old_status != 'Completed' and new_status == 'Completed':
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        part = form.cleaned_data['part']
                        quantity = form.cleaned_data['quantity']
                        if part.quantity < quantity:
                            form.add_error('quantity', f"Only {part.quantity} in stock for '{part.name}'.")
                            return render(request, 'repairs/repair_form.html', {
                                'form': repair_form,
                                'formset': formset,
                                'title': 'Edit Repair'
                            })

            # Save the repair and parts
            repair = repair_form.save()
            formset.save()

            print("DEBUG: OLD STATUS =", old_status)
            print("DEBUG: NEW STATUS =", repair.status)
            print("DEBUG: Parts linked to repair =", RepairPart.objects.filter(repair=repair).count())

            # Only deduct if changing from non-Completed to Completed
            if old_status != 'Completed' and repair.status == 'Completed':
                print(f"DEBUG: Deducting for repair {repair.id}")
                for rp in RepairPart.objects.filter(repair=repair):
                    print(f"→ {rp.part.name}: -{rp.quantity} (was {rp.part.quantity})")
                    rp.part.quantity -= rp.quantity
                    rp.part.save()
                    print(f"→ Now {rp.part.quantity} remaining")

            return redirect('repair_list')

    else:
        repair_form = RepairRecordForm(instance=repair)
        formset = RepairPartFormSet(instance=repair)

    return render(request, 'repairs/repair_form.html', {
        'form': repair_form,
        'formset': formset,
        'title': 'Edit Repair'
    })

from django.contrib import messages

@login_required
def delete_repair(request, pk):
    repair = get_object_or_404(RepairRecord, pk=pk)

    if request.method == 'POST':
        repair.delete()
        messages.success(request, 'Repair record deleted successfully.')
        return redirect('repair_list')

    return render(request, 'repairs/confirm_delete.html', {
        'object': repair,
        'title': 'Delete Repair'
    })

@login_required
def motorcycle_model_list(request):
    models = MotorcycleModel.objects.all().order_by('name')
    return render(request, 'repairs/motorcycle_model_list.html', {'models': models})

@login_required
def add_motorcycle_model(request):
    if request.method == 'POST':
        form = MotorcycleModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('motorcycle_model_list')
    else:
        form = MotorcycleModelForm()
    return render(request, 'repairs/motorcycle_model_form.html', {'form': form, 'title': 'Add Motorcycle Model'})

@login_required
def edit_motorcycle_model(request, pk):
    model = get_object_or_404(MotorcycleModel, pk=pk)
    if request.method == 'POST':
        form = MotorcycleModelForm(request.POST, instance=model)
        if form.is_valid():
            form.save()
            return redirect('motorcycle_model_list')
    else:
        form = MotorcycleModelForm(instance=model)
    return render(request, 'repairs/motorcycle_model_form.html', {'form': form, 'title': 'Edit Motorcycle Model'})

@login_required
def delete_motorcycle_model(request, pk):
    model = get_object_or_404(MotorcycleModel, pk=pk)
    if request.method == 'POST':
        model.delete()
        return redirect('motorcycle_model_list')
    return render(request, 'repairs/confirm_delete.html', {'object': model, 'title': 'Delete Motorcycle Model'})

@login_required
def motorcycle_list(request):
    motorcycles = Motorcycle.objects.select_related('customer', 'model').order_by('-id')
    return render(request, 'repairs/motorcycle_list.html', {'motorcycles': motorcycles})

@login_required
def add_motorcycle(request):
    if request.method == 'POST':
        form = MotorcycleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('motorcycle_list')
    else:
        form = MotorcycleForm()
    return render(request, 'repairs/motorcycle_form.html', {'form': form, 'title': 'Add Motorcycle'})

@login_required
def edit_motorcycle(request, pk):
    motorcycle = get_object_or_404(Motorcycle, pk=pk)
    if request.method == 'POST':
        form = MotorcycleForm(request.POST, instance=motorcycle)
        if form.is_valid():
            form.save()
            return redirect('motorcycle_list')
    else:
        form = MotorcycleForm(instance=motorcycle)
    return render(request, 'repairs/motorcycle_form.html', {'form': form, 'title': 'Edit Motorcycle'})

@login_required
def delete_motorcycle(request, pk):
    motorcycle = get_object_or_404(Motorcycle, pk=pk)
    if request.method == 'POST':
        motorcycle.delete()
        return redirect('motorcycle_list')
    return render(request, 'repairs/confirm_delete.html', {'object': motorcycle, 'title': 'Delete Motorcycle'})