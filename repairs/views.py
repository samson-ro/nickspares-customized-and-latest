from django.shortcuts import render, get_object_or_404, redirect
from .models import RepairRecord, RepairPart
from .forms import RepairPartFormSet, RepairRecordForm, RepairPartForm
from django.forms import inlineformset_factory

from django.contrib.auth.decorators import login_required

# List all repair records
@login_required
def repair_list(request):
    repairs = RepairRecord.objects.all().order_by('-date_in')
    return render(request, 'repairs/repair_list.html', {'repairs': repairs})

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
            # Check stock availability for all parts
            for part_form in formset:
                if part_form.cleaned_data and not part_form.cleaned_data.get('DELETE'):
                    part = part_form.cleaned_data['part']
                    quantity = part_form.cleaned_data['quantity']
                    if part.quantity < quantity:
                        part_form.add_error('quantity', 
                                            f"Only {part.quantity} in stock for '{part.name}'.")
                        return render(request, 'repairs/repair_form.html', {
                            'form': form,
                            'formset': formset,
                            'title': 'Add Repair'
                        })

            # Save repair and deduct stock
            repair = form.save()
            parts = formset.save(commit=False)
            for part in parts:
                part.repair = repair
                part.save()

                # Deduct sparepart from Inventory
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


#Editing repairs
@login_required
def edit_repair(request, pk):
    repair = get_object_or_404(RepairRecord, pk=pk)
    RepairPartFormSet = inlineformset_factory(
        RepairRecord,
        RepairPart,
        form=RepairPartForm,
        extra=2, #Can be any number(no of items that can be editted at a given time)
        can_delete=True
    )

    # Save original parts and their quantities
    original_parts_qs = RepairPart.objects.filter(repair=repair)
    original_parts = {rp.pk: rp.quantity for rp in original_parts_qs}
    original_parts_instances = {rp.pk: rp for rp in original_parts_qs}

    if request.method == 'POST':
        repair_form = RepairRecordForm(request.POST, instance=repair)
        formset = RepairPartFormSet(request.POST, instance=repair)

        if repair_form.is_valid() and formset.is_valid():
            
            # Revert inventory for original parts
            for rp in original_parts_qs:
                rp.part.quantity += rp.quantity
                rp.part.save()

            # Validate stock for new parts
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

            # Save form and formset
            repair = repair_form.save()
            formset.save()

            # Deduct updated part quantities
            for rp in RepairPart.objects.filter(repair=repair):
                rp.part.quantity -= rp.quantity
                rp.part.save()

            return redirect('repair_list')

    else:
        repair_form = RepairRecordForm(instance=repair)
        formset = RepairPartFormSet(instance=repair)

    return render(request, 'repairs/repair_form.html', {
        'form': repair_form,
        'formset': formset,
        'title': 'Edit Repair'
    })

# Delete a repair record
@login_required
def delete_repair(request, pk):
    repair = get_object_or_404(RepairRecord, pk=pk)

    if request.method == 'POST':
        # Restore inventory for all parts used in this repair
        for repair_part in repair.repairpart_set.all():
            spare_part = repair_part.part
            spare_part.quantity += repair_part.quantity
            spare_part.save()

        # Delete the repair
        repair.delete()
        return redirect('repair_list')

    return render(request, 'repairs/confirm_delete.html', {
        'object': repair,
        'title': 'Delete Repair'
    })
