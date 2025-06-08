from django.shortcuts import render, get_object_or_404, redirect
from .models import SparePart
from .forms import SparePartForm
from django.contrib.auth.decorators import login_required

@login_required
def sparepart_list(request):
    parts = SparePart.objects.all().order_by('-date_added')
    return render(request, 'inventory/sparepart_list.html', {'parts': parts})

@login_required
def sparepart_detail(request, pk):
    sparepart = get_object_or_404(SparePart, pk=pk)
    return render(request, 'inventory/sparepart_detail.html', {'sparepart': sparepart})

@login_required
def add_sparepart(request):
    if request.method == 'POST':
        form = SparePartForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sparepart_list')
    else:
        form = SparePartForm()
    return render(request, 'inventory/sparepart_form.html', {'form': form, 'title': 'Add Spare Part'})

@login_required
def edit_sparepart(request, pk):
    part = get_object_or_404(SparePart, pk=pk)
    if request.method == 'POST':
        form = SparePartForm(request.POST, instance=part)
        if form.is_valid():
            form.save()
            return redirect('sparepart_list')
    else:
        form = SparePartForm(instance=part)
    return render(request, 'inventory/sparepart_form.html', {'form': form, 'title': 'Edit Spare Part'})

@login_required
def delete_sparepart(request, pk):
    part = get_object_or_404(SparePart, pk=pk)
    if request.method == 'POST':
        part.delete()
        return redirect('sparepart_list')
    return render(request, 'inventory/confirm_delete.html', {'object': part, 'title': 'Delete Spare Part'})