from django.shortcuts import render, get_object_or_404, redirect
from repairs.models import RepairPart
from .models import Invoice, SparePartPurchase
from .forms import InvoiceForm, SparePartPurchaseFormSet, SparePartPurchaseForm
from inventory.models import SparePart
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory


@login_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('customer', 
                                              'repair').order_by('-date_issued')
    
    # Create a list with additional context for each invoice
    enriched_invoices = []
    for invoice in invoices:
        if invoice.repair:
            enriched_invoices.append({
                'invoice': invoice,
                'type': 'Repair',
                'details': invoice.repair.work_done  # or any other detail i'll want
            })
        else:
            purchases = SparePartPurchase.objects.filter(invoice=invoice).select_related('part')
            enriched_invoices.append({
                'invoice': invoice,
                'type': 'Purchase',
                'details': purchases
            })

    return render(request, 'billing/invoice_list.html', {
        'invoices': enriched_invoices
    })


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 
                  'billing/invoice_detail.html', 
                  {'invoice': invoice })


@login_required
def add_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)

            # Calculating parts total
            parts = RepairPart.objects.filter(repair=invoice.repair)
            parts_total = sum(part.quantity * part.part.price for part in parts)

            # Add cost of service
            invoice.amount = parts_total + invoice.repair.cost_of_service
            invoice.save()

            return redirect('invoice_list')
    else:
        form = InvoiceForm()
        total_amount = None

    return render(request, 'billing/invoice_form.html', {
        'form': form,
        'title': 'Add Invoice',
        'total_amount': total_amount
    })



@login_required
def edit_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    is_purchase = invoice.repair is None  # Checking to see if it's a spare part purchase

    PurchaseFormSet = inlineformset_factory(
        Invoice,
        SparePartPurchase,
        form=SparePartPurchaseForm,
        extra=1, #can be more
        can_delete=True
    )

    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = PurchaseFormSet(request.POST, instance=invoice) if is_purchase else None

        if form.is_valid() and (formset is None or formset.is_valid()):
            form.save()
            if formset:
                formset.save()
            return redirect('invoice_list')
    else:
        form = InvoiceForm(instance=invoice)
        formset = PurchaseFormSet(instance=invoice) if is_purchase else None

    return render(request, 'billing/invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Edit Invoice',
        'invoice': invoice  # so the template can check
    })


@login_required
def delete_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        return redirect('invoice_list')
    return render(request, 'billing/confirm_delete.html', {'object': invoice, 'title': 'Delete Invoice'})


@login_required
def purchase_spare_parts(request):
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST)
        formset = SparePartPurchaseFormSet(request.POST, queryset=SparePartPurchase.objects.none())

        if invoice_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    #Create an invoice if there is no repair
                    invoice = invoice_form.save(commit=False)
                    invoice.repair = None  # Standalone purchase hence has to be none
                    invoice.amount = 0  # To be calculated automatically
                    invoice.save()

                    #TODO GO THROUGH TO MAKE SURE THAT NOONE CAN PERFORM ACTIONS ON A DEPLETED INVENTORY ITEM
                    total = 0
                    for form in formset:
                        if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                            part = form.cleaned_data['part']
                            quantity = form.cleaned_data['quantity']

                            if part.quantity < quantity:
                                form.add_error('quantity', f"Not enough in stock for {part.name}")
                                raise ValueError("Insufficient stock")

                            # Deduct sparepart from inventory
                            part.quantity -= quantity
                            part.save()

                            # Calculate cost
                            total += part.price * quantity

                            # Save purchase record
                            purchase = form.save(commit=False)
                            purchase.invoice = invoice
                            purchase.save()

                    # Save updated total amount to invoice
                    invoice.amount = total
                    invoice.save()

                    messages.success(request, "Purchase completed successfully.")
                    return redirect('invoice_list')

            except Exception as e:
                messages.error(request, f"Purchase cannot be completed: {str(e)}")
    else:
        invoice_form = InvoiceForm()
        formset = SparePartPurchaseFormSet(queryset=SparePartPurchase.objects.none())

    return render(request, 'billing/purchase_form.html', {
        'invoice_form': invoice_form,
        'formset': formset,
        'title': 'Purchase Spare Parts'
    })
