from django.shortcuts import render, get_object_or_404, redirect
from .models import SparePart, Supplier, PartCategory
from .forms import SparePartForm, SupplierForm, PartCategoryForm
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

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

@login_required
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'inventory/supplier_form.html', {'form': form, 'title': 'Add Supplier'})

@login_required
def edit_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'inventory/supplier_form.html', {'form': form, 'title': 'Edit Supplier'})

@login_required
def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_list')
    return render(request, 'inventory/confirm_delete.html', {'object': supplier, 'title': 'Delete Supplier'})

@login_required
def partcategory_list(request):
    categories = PartCategory.objects.all().order_by('name')
    return render(request, 'inventory/partcategory_list.html', {'categories': categories})

@login_required
def add_partcategory(request):
    if request.method == 'POST':
        form = PartCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('partcategory_list')
    else:
        form = PartCategoryForm()
    return render(request, 'inventory/partcategory_form.html', {'form': form, 'title': 'Add Part Category'})

@login_required
def edit_partcategory(request, pk):
    category = get_object_or_404(PartCategory, pk=pk)
    if request.method == 'POST':
        form = PartCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('partcategory_list')
    else:
        form = PartCategoryForm(instance=category)
    return render(request, 'inventory/partcategory_form.html', {'form': form, 'title': 'Edit Part Category'})

@login_required
def delete_partcategory(request, pk):
    category = get_object_or_404(PartCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('partcategory_list')
    return render(request, 'inventory/confirm_delete.html', {'object': category, 'title': 'Delete Part Category'})