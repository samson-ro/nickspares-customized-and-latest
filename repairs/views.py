from django.shortcuts import render, get_object_or_404, redirect
from .models import RepairRecord, RepairPart
from .forms import RepairPartFormSet, RepairRecordForm, RepairPartForm
from django.forms import inlineformset_factory
from .models import RepairRecord
from django.contrib.auth.decorators import login_required

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

# Add a new repair record
@login_required
def add_repair(request):
    if request.method == 'POST':
        form = RepairRecordForm(request.POST)
        formset = RepairPartFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            repair = form.save(commit=False)
            
            # Only check stock if status is being set to Completed
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
            
            # Save the repair first
            repair.save()
            
            # Process parts and deduct inventory only if status is Completed
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