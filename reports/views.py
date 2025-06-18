from inventory.models import SparePart
from billing.models import PurchasedPart
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from billing.models import Invoice
from .utils import calculate_profit_by_month, calculate_total_profit, render_pdf_view, parse_date_range
from django.db.models import Sum, Count

from customers.models import Customer

from django.db.models.functions import TruncMonth
from django.utils.dateformat import DateFormat

from repairs.models import RepairRecord, RepairPart, Motorcycle

from collections import defaultdict

from django.utils.timezone import make_naive

from django.utils.timezone import make_aware
import datetime

from django.shortcuts import get_object_or_404
from employees.models import Employee

from inventory.models import Supplier
from django.utils.timezone import now, timedelta


@login_required
def invoice_report(request):
    from_date, to_date = parse_date_range(request)
    invoices = Invoice.objects.select_related('customer', 'repair')

    if from_date:
        invoices = invoices.filter(date_issued__gte=from_date)
    if to_date:
        invoices = invoices.filter(date_issued__lte=to_date)

    context = {
        "invoices": invoices,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view("reports/invoice_reports/invoice_report_pdf.html", context, "invoice-report.pdf")

    return render(request, "reports/invoice_reports/invoice_report.html", context)

@login_required
def unpaid_invoices_report(request):
    from_date, to_date = parse_date_range(request)

    invoices = Invoice.objects.select_related('customer').filter(paid=False)

    if from_date:
        invoices = invoices.filter(date_issued__gte=from_date)
    if to_date:
        invoices = invoices.filter(date_issued__lte=to_date)

    context = {
        "invoices": invoices,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view("reports/invoice_reports/unpaid_invoices_report_pdf.html", context, "unpaid-invoices.pdf")

    return render(request, "reports/invoice_reports/unpaid_invoices_report.html", context)

@login_required
def payment_summary_report(request):
    from_date, to_date = parse_date_range(request)

    invoices = Invoice.objects.filter(paid=True)

    if from_date:
        invoices = invoices.filter(date_issued__gte=from_date)
    if to_date:
        invoices = invoices.filter(date_issued__lte=to_date)

    # Group totals by payment method
    summary = invoices.values('payment_method').annotate(total=Sum('amount'))

    summary_dict = {item['payment_method']: item['total'] for item in summary}

    context = {
        "summary": summary_dict,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view("reports/invoice_reports/payment_summary_report_pdf.html", context, "payment-summary.pdf")

    return render(request, "reports/invoice_reports/payment_summary_report.html", context)

@login_required
def customer_invoice_history(request):
    from_date, to_date = parse_date_range(request)
    customer_id = request.GET.get("customer_id")

    customers = Customer.objects.all()
    invoices = []
    customer = None

    if customer_id:
        invoices = Invoice.objects.filter(customer_id=customer_id)
        customer = Customer.objects.filter(id=customer_id).first()

        if from_date:
            invoices = invoices.filter(date_issued__gte=from_date)
        if to_date:
            invoices = invoices.filter(date_issued__lte=to_date)

    context = {
        "invoices": invoices,
        "from_date": from_date,
        "to_date": to_date,
        "customers": customers,
        "customer": customer,
    }

    if request.GET.get("format") == "pdf" and customer:
        return render_pdf_view("reports/invoice_reports/customer_invoice_history_pdf.html", context, "customer-invoice-history.pdf")

    return render(request, "reports/invoice_reports/customer_invoice_history.html", context)

@login_required
def top_customers_report(request):
    from_date, to_date = parse_date_range(request)

    invoices = Invoice.objects.filter(paid=True)

    if from_date:
        invoices = invoices.filter(date_issued__gte=from_date)
    if to_date:
        invoices = invoices.filter(date_issued__lte=to_date)

    # Aggregate totals per customer
    totals = invoices.values('customer').annotate(total=Sum('amount')).order_by('-total')

    # Fetch customer instances
    customer_ids = [item['customer'] for item in totals]
    customer_map = {c.id: c for c in Customer.objects.filter(id__in=customer_ids)}

    # Pair customer object with total
    top_customers = [(customer_map[item['customer']], item['total']) for item in totals]

    context = {
        "top_customers": top_customers,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view("reports/invoice_reports/top_customers_report_pdf.html", context, "top-customers.pdf")

    return render(request, "reports/invoice_reports/top_customers_report.html", context)


@login_required
def monthly_invoice_breakdown(request):
    from_date, to_date = parse_date_range(request)
    invoices = Invoice.objects.filter(paid=True)

    if from_date:
        invoices = invoices.filter(date_issued__gte=from_date)
    if to_date:
        invoices = invoices.filter(date_issued__lte=to_date)

    # Group by month
    grouped = invoices.annotate(month=TruncMonth('date_issued')).values('month').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('month')

    # Format month names
    monthly_data = {}
    for entry in grouped:
        month_label = DateFormat(entry['month']).format('F Y')  # e.g. March 2025
        monthly_data[month_label] = {
            'count': entry['count'],
            'total': entry['total']
        }

    context = {
        'monthly_data': monthly_data,
        'from_date': from_date,
        'to_date': to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view("reports/invoice_reports/monthly_invoice_breakdown_pdf.html", context, "monthly-invoice-breakdown.pdf")

    return render(request, "reports/invoice_reports/monthly_invoice_breakdown.html", context)


@login_required
def part_sales_report(request):
    from_date, to_date = parse_date_range(request)

    parts_qs = PurchasedPart.objects.select_related('part', 'invoice').filter(invoice__paid=True)

    if from_date:
        parts_qs = parts_qs.filter(invoice__date_issued__gte=from_date)
    if to_date:
        parts_qs = parts_qs.filter(invoice__date_issued__lte=to_date)

    # Group by SparePart
    part_sales = {}

    for item in parts_qs:
        part = item.part
        if part not in part_sales:
            part_sales[part] = {"quantity": 0, "revenue": 0}
        part_sales[part]["quantity"] += item.quantity
        part_sales[part]["revenue"] += item.quantity * item.price

    context = {
        "part_sales": part_sales,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view("reports/invoice_reports/part_sales_report_pdf.html", context, "part-sales-report.pdf")

    return render(request, "reports/invoice_reports/part_sales_report.html", context)



@login_required
def repair_summary_report(request):
    from_date, to_date = parse_date_range(request)

    repairs = RepairRecord.objects.select_related('customer', 'motorcycle__model', 'mechanic')

    if from_date:
        repairs = repairs.filter(date_in__gte=from_date)
    if to_date:
        repairs = repairs.filter(date_in__lte=to_date)

    context = {
        "repairs": repairs,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view("reports/repair_reports/repair_summary_report_pdf.html", context, "repair-summary.pdf")

    return render(request, "reports/repair_reports/repair_summary_report.html", context)

@login_required
def top_models_report(request):
    from_date, to_date = parse_date_range(request)

    repairs = RepairRecord.objects.select_related('motorcycle__model')

    if from_date:
        repairs = repairs.filter(date_in__gte=from_date)
    if to_date:
        repairs = repairs.filter(date_in__lte=to_date)

    report_data = defaultdict(lambda: {"count": 0, "total": 0})

    for repair in repairs:
        if repair.motorcycle and repair.motorcycle.model:
            model_name = repair.motorcycle.model.name
            report_data[model_name]["count"] += 1
            report_data[model_name]["total"] += repair.cost_of_service

    context = {
        "report_data": dict(sorted(report_data.items(), key=lambda x: x[1]["count"], reverse=True)),
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view("reports/repair_reports/top_models_report_pdf.html", context, "top-repaired-models.pdf")

    return render(request, "reports/repair_reports/top_models_report.html", context) 

@login_required
def repair_revenue_report(request):
    from_date, to_date = parse_date_range(request)

    repairs = RepairRecord.objects.all()
    if from_date:
        repairs = repairs.filter(date_in__gte=from_date)
    if to_date:
        repairs = repairs.filter(date_in__lte=to_date)

    total_service = repairs.aggregate(Sum('cost_of_service'))['cost_of_service__sum'] or 0

    # Get RepairPart data only for repairs in the filtered queryset
    repair_ids = repairs.values_list('id', flat=True)
    parts = RepairPart.objects.filter(repair_id__in=repair_ids).select_related('part')

    total_parts = sum(rp.quantity * rp.part.price for rp in parts)

    context = {
        'from_date': from_date,
        'to_date': to_date,
        'total_service': total_service,
        'total_parts': total_parts,
        'total_combined': total_service + total_parts
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view("reports/repair_reports/repair_revenue_report_pdf.html", context, "repair-revenue.pdf")

    return render(request, "reports/repair_reports/repair_revenue_report.html", context)

@login_required
def most_common_repairs_report(request):
    from_date, to_date = parse_date_range(request)

    repairs = RepairRecord.objects.all()

    if from_date:
        repairs = repairs.filter(date_in__gte=from_date)
    if to_date:
        repairs = repairs.filter(date_in__lte=to_date)

    repair_stats = defaultdict(lambda: {"count": 0, "total": 0})

    for r in repairs:
        complaint = (r.complaint or "").strip().lower()
        if complaint:
            repair_stats[complaint]["count"] += 1
            repair_stats[complaint]["total"] += r.cost_of_service

    # Sort by count descending
    sorted_stats = dict(sorted(repair_stats.items(), key=lambda x: x[1]["count"], reverse=True))

    context = {
        "repair_stats": sorted_stats,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view("reports/repair_reports/most_common_repairs_report_pdf.html", context, "most-common-repairs.pdf")

    return render(request, "reports/repair_reports/most_common_repairs_report.html", context)

@login_required
def repair_parts_usage_report(request):
    from_date, to_date = parse_date_range(request)

    # Get repair IDs within date range
    repairs = RepairRecord.objects.all()
    if from_date:
        repairs = repairs.filter(date_in__gte=from_date)
    if to_date:
        repairs = repairs.filter(date_in__lte=to_date)

    repair_ids = repairs.values_list('id', flat=True)

    parts = RepairPart.objects.filter(repair_id__in=repair_ids).select_related('part')
    part_usage = defaultdict(lambda: {"quantity": 0, "total": 0})

    for item in parts:
        part_name = item.part.name
        part_usage[part_name]["quantity"] += item.quantity
        part_usage[part_name]["total"] += item.quantity * item.part.price

    context = {
        "from_date": from_date,
        "to_date": to_date,
        "part_usage": dict(sorted(part_usage.items(), key=lambda x: x[1]["quantity"], reverse=True)),
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view("reports/repair_reports/repair_parts_usage_report_pdf.html", context, "repair-parts-usage.pdf")

    return render(request, "reports/repair_reports/repair_parts_usage_report.html", context)

@login_required
def average_repair_time_report(request):
    from_date, to_date = parse_date_range(request)

    # Get only completed repairs
    repairs = RepairRecord.objects.exclude(date_out__isnull=True).select_related("customer", "motorcycle")

    if from_date:
        repairs = repairs.filter(date_in__gte=from_date)
    if to_date:
        repairs = repairs.filter(date_in__lte=to_date)

    completed_repairs = []
    total_hours = 0

    for repair in repairs:
        # Calculate naive durations (timezone-safe)
        date_in = make_naive(repair.date_in)
        date_out = make_naive(repair.date_out)
        duration = (date_out - date_in).total_seconds() / 3600  # in hours

        if duration >= 0:
            repair.duration = duration  # add dynamic field
            completed_repairs.append(repair)
            total_hours += duration

    avg_duration = total_hours / len(completed_repairs) if completed_repairs else 0

    context = {
        "from_date": from_date,
        "to_date": to_date,
        "repairs": completed_repairs,
        "avg_duration": avg_duration
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/repair_reports/average_repair_time_report_pdf.html",
            context,
            "average-repair-time.pdf"
        )

    return render(request, "reports/repair_reports/average_repair_time_report.html", context)

@login_required
def inventory_summary_report(request):
    parts = SparePart.objects.select_related("category", "supplier").all()

    # Annotate with total_value
    for part in parts:
        part.total_value = part.quantity * part.price

    context = {
        "parts": parts
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/inventory_reports/inventory_summary_report_pdf.html",
            context,
            "inventory-summary.pdf"
        )

    return render(request, "reports/inventory_reports/inventory_summary_report.html", context)

@login_required
def low_stock_report(request):
    from_date, to_date = parse_date_range(request)

    parts = SparePart.objects.select_related("category", "supplier").filter(quantity__lte=5)

    if from_date:
        parts = parts.filter(date_added__date__gte=from_date)
    if to_date:
        parts = parts.filter(date_added__date__lte=to_date)

    for part in parts:
        part.total_value = part.quantity * part.price

    context = {
        "parts": parts,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/inventory_reports/low_stock_report_pdf.html",
            context,
            "low-stock-report.pdf"
        )

    return render(request, "reports/inventory_reports/low_stock_report.html", context)

@login_required
def supplier_inventory_report(request):
    from_date, to_date = parse_date_range(request)

    parts = SparePart.objects.select_related("supplier").all()

    if from_date:
        parts = parts.filter(date_added__date__gte=from_date)
    if to_date:
        parts = parts.filter(date_added__date__lte=to_date)

    # Annotate total_value and group by supplier
    supplier_parts = defaultdict(list)
    for part in parts:
        part.total_value = part.quantity * part.price
        supplier_name = part.supplier.name if part.supplier else "Unknown Supplier"
        supplier_parts[supplier_name].append(part)

    context = {
        "supplier_parts": dict(supplier_parts),
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/inventory_reports/supplier_inventory_report_pdf.html",
            context,
            "supplier-inventory.pdf"
        )

    return render(request, "reports/inventory_reports/supplier_inventory_report.html", context)

@login_required
def category_inventory_report(request):
    from_date, to_date = parse_date_range(request)

    parts = SparePart.objects.select_related("category").all()

    if from_date:
        parts = parts.filter(date_added__date__gte=from_date)
    if to_date:
        parts = parts.filter(date_added__date__lte=to_date)

    category_parts = defaultdict(list)

    for part in parts:
        part.total_value = part.quantity * part.price
        cat_name = part.category.name if part.category else "Uncategorized"
        category_parts[cat_name].append(part)

    context = {
        "category_parts": dict(category_parts),
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/inventory_reports/category_inventory_report_pdf.html",
            context,
            "category-inventory.pdf"
        )

    return render(request, "reports/inventory_reports/category_inventory_report.html", context)

@login_required
def price_list_report(request):
    from_date, to_date = parse_date_range(request)

    parts = SparePart.objects.select_related("category", "supplier").all()

    if from_date:
        parts = parts.filter(date_added__date__gte=from_date)
    if to_date:
        parts = parts.filter(date_added__date__lte=to_date)

    for part in parts:
        part.total_value = part.quantity * part.price

    # Sort by unit price descending
    parts = sorted(parts, key=lambda p: p.price, reverse=True)

    context = {
        "parts": parts,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/inventory_reports/price_list_report_pdf.html",
            context,
            "price-list.pdf"
        )

    return render(request, "reports/inventory_reports/price_list_report.html", context)

from django.db.models import F, ExpressionWrapper, DecimalField

@login_required
def inventory_value_over_time(request):
    from_date, to_date = parse_date_range(request)

    parts = SparePart.objects.all()

    if from_date:
        from_dt = make_aware(datetime.datetime.combine(from_date, datetime.time.min))
        parts = parts.filter(date_added__gte=from_dt)

    if to_date:
        to_dt = make_aware(datetime.datetime.combine(to_date, datetime.time.max))
        parts = parts.filter(date_added__lte=to_dt)

    data = (
        parts.annotate(month=TruncMonth("date_added"))
             .values("month")
             .annotate(
                 total_parts=Count("id"),
                 total_value=Sum(
                     ExpressionWrapper(F("quantity") * F("price"), output_field=DecimalField()))
             )
             .order_by("month")
    )

    context = {
        "data": data,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/inventory_reports/inventory_value_over_time_pdf.html",
            context,
            "inventory-value-over-time.pdf"
        )

    return render(request, "reports/inventory_reports/inventory_value_over_time.html", context)

@login_required
def customer_summary_report(request):
    from_date, to_date = parse_date_range(request)

    customers = Customer.objects.all()

    if from_date:
        customers = customers.filter(date_created__date__gte=from_date)
    if to_date:
        customers = customers.filter(date_created__date__lte=to_date)

    context = {
        "customers": customers,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/customer_reports/customer_summary_report_pdf.html",
            context,
            "customer-summary.pdf"
        )

    return render(request, "reports/customer_reports/customer_summary_report.html", context)

@login_required
def top_customers_by_revenue(request):
    from_date, to_date = parse_date_range(request)

    invoices = Invoice.objects.select_related("customer")

    if from_date:
        invoices = invoices.filter(date_issued__date__gte=from_date)
    if to_date:
        invoices = invoices.filter(date_issued__date__lte=to_date)

    top_customers = (
        invoices.values("customer__name")
        .annotate(
            total_revenue=Sum("amount"),
            invoice_count=Count("id")
        )
        .order_by("-total_revenue")
    )

    context = {
        "top_customers": top_customers,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/customer_reports/top_customers_by_revenue_pdf.html",
            context,
            "top-customers.pdf"
        )

    return render(request, "reports/customer_reports/top_customers_by_revenue.html", context)

@login_required
def customers_with_most_repairs(request):
    from_date, to_date = parse_date_range(request)

    repairs = RepairRecord.objects.select_related("customer")

    if from_date:
        repairs = repairs.filter(date_in__date__gte=from_date)
    if to_date:
        repairs = repairs.filter(date_in__date__lte=to_date)

    ranked_customers = (
        repairs.values("customer__name")
        .annotate(
            total_repairs=Count("id"),
            total_cost=Sum("cost_of_service")
        )
        .order_by("-total_repairs")
    )

    context = {
        "ranked_customers": ranked_customers,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/customer_reports/customers_with_most_repairs_pdf.html",
            context,
            "most-repairs.pdf"
        )

    return render(request, "reports/customer_reports/customers_with_most_repairs.html", context)

@login_required
def new_customers_over_time(request):
    from_date, to_date = parse_date_range(request)

    customers = Customer.objects.all()

    if from_date:
        customers = customers.filter(date_created__date__gte=from_date)
    if to_date:
        customers = customers.filter(date_created__date__lte=to_date)

    monthly_data = (
        customers.annotate(month=TruncMonth("date_created"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    context = {
        "monthly_data": monthly_data,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/customer_reports/new_customers_over_time_pdf.html",
            context,
            "new-customers.pdf"
        )

    return render(request, "reports/customer_reports/new_customers_over_time.html", context)

@login_required
def customer_service_history(request):
    customer_id = request.GET.get("customer")
    from_date, to_date = parse_date_range(request)

    customers = Customer.objects.all()

    selected_customer = None
    repairs = []
    invoices = []
    motorcycles = []

    if customer_id:
        selected_customer = get_object_or_404(Customer, id=customer_id)
        repairs = RepairRecord.objects.filter(customer=selected_customer)
        invoices = Invoice.objects.filter(customer=selected_customer)
        motorcycles = Motorcycle.objects.filter(customer=selected_customer)

        if from_date:
            repairs = repairs.filter(date_in__date__gte=from_date)
            invoices = invoices.filter(date_issued__date__gte=from_date)
        if to_date:
            repairs = repairs.filter(date_in__date__lte=to_date)
            invoices = invoices.filter(date_issued__date__lte=to_date)

    context = {
        "customers": customers,
        "selected_customer": selected_customer,
        "repairs": repairs,
        "invoices": invoices,
        "motorcycles": motorcycles,
        "from_date": from_date,
        "to_date": to_date,
    }

    if request.GET.get("format") == "pdf" and selected_customer:
        return render_pdf_view(
            "reports/customer_reports/customer_service_history_pdf.html",
            context,
            f"{selected_customer.name}-service-history.pdf"
        )

    return render(request, "reports/customer_reports/customer_service_history.html", context)

@login_required
def employee_summary_report(request):
    from_date, to_date = parse_date_range(request)

    employees = Employee.objects.all()

    if from_date:
        employees = employees.filter(hire_date__gte=from_date)
    if to_date:
        employees = employees.filter(hire_date__lte=to_date)

    context = {
        "employees": employees,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/employee_reports/employee_summary_report_pdf.html",
            context,
            "employee-summary.pdf"
        )

    return render(request, "reports/employee_reports/employee_summary_report.html", context)

@login_required
def repair_count_by_mechanic(request):
    from_date, to_date = parse_date_range(request)

    repairs = RepairRecord.objects.select_related("mechanic").filter(mechanic__isnull=False)

    if from_date:
        repairs = repairs.filter(date_in__date__gte=from_date)
    if to_date:
        repairs = repairs.filter(date_in__date__lte=to_date)

    mechanic_data = (
        repairs.values("mechanic__name")
        .annotate(
            total_repairs=Count("id"),
            total_cost=Sum("cost_of_service")
        )
        .order_by("-total_repairs")
    )

    context = {
        "mechanic_data": mechanic_data,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/employee_reports/repair_count_by_mechanic_pdf.html",
            context,
            "repair-count-by-mechanic.pdf"
        )

    return render(request, "reports/employee_reports/repair_count_by_mechanic.html", context)

@login_required
def mechanic_workload_detail(request):
    from_date, to_date = parse_date_range(request)
    mechanic_id = request.GET.get("mechanic")

    mechanics = Employee.objects.all()
    selected_mechanic = None
    repairs = []

    if mechanic_id:
        selected_mechanic = get_object_or_404(Employee, id=mechanic_id)
        repairs = RepairRecord.objects.filter(mechanic=selected_mechanic)

        if from_date:
            repairs = repairs.filter(date_in__date__gte=from_date)
        if to_date:
            repairs = repairs.filter(date_in__date__lte=to_date)

    context = {
        "mechanics": mechanics,
        "selected_mechanic": selected_mechanic,
        "repairs": repairs,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf" and selected_mechanic:
        return render_pdf_view(
            "reports/employee_reports/mechanic_workload_detail_pdf.html",
            context,
            f"{selected_mechanic.name}-workload.pdf"
        )

    return render(request, "reports/employee_reports/mechanic_workload_detail.html", context)

@login_required
def monthly_repair_output(request):
    from_date, to_date = parse_date_range(request)

    repairs = RepairRecord.objects.select_related("mechanic").filter(mechanic__isnull=False)

    if from_date:
        repairs = repairs.filter(date_in__date__gte=from_date)
    if to_date:
        repairs = repairs.filter(date_in__date__lte=to_date)

    monthly_output = (
        repairs.annotate(month=TruncMonth("date_in"))
        .values("month", "mechanic__name")
        .annotate(
            repair_count=Count("id"),
            total_revenue=Sum("cost_of_service")
        )
        .order_by("month", "-repair_count")
    )

    context = {
        "monthly_output": monthly_output,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/employee_reports/monthly_repair_output_pdf.html",
            context,
            "monthly-repair-output.pdf"
        )

    return render(request, "reports/employee_reports/monthly_repair_output.html", context)

@login_required
def top_performing_mechanics(request):
    from_date, to_date = parse_date_range(request)

    repairs = RepairRecord.objects.select_related("mechanic").filter(mechanic__isnull=False)

    if from_date:
        repairs = repairs.filter(date_in__date__gte=from_date)
    if to_date:
        repairs = repairs.filter(date_in__date__lte=to_date)

    performance = (
        repairs.values("mechanic__name")
        .annotate(
            total_revenue=Sum("cost_of_service"),
            total_repairs=Count("id")
        )
        .order_by("-total_revenue")
    )

    context = {
        "performance": performance,
        "from_date": from_date,
        "to_date": to_date
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/employee_reports/top_performing_mechanics_pdf.html",
            context,
            "top-mechanics.pdf"
        )

    return render(request, "reports/employee_reports/top_performing_mechanics.html", context)

@login_required
def supplier_summary_report(request):
    suppliers = Supplier.objects.all()

    context = {
        "suppliers": suppliers
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/supplier_reports/supplier_summary_report_pdf.html",
            context,
            "supplier-summary.pdf"
        )

    return render(request, "reports/supplier_reports/supplier_summary_report.html", context)

@login_required
def parts_supplied_per_supplier(request):
    supplier_stats = (
        SparePart.objects
        .filter(supplier__isnull=False)
        .values("supplier__name")
        .annotate(
            total_parts=Count("id"),
            total_value=Sum(F("price") * F("quantity"))
        )
        .order_by("-total_value")
    )

    context = {
        "supplier_stats": supplier_stats
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/supplier_reports/parts_supplied_per_supplier_pdf.html",
            context,
            "parts-by-supplier.pdf"
        )

    return render(request, "reports/supplier_reports/parts_supplied_per_supplier.html", context)

@login_required
def top_suppliers_by_value(request):
    suppliers = (
        SparePart.objects
        .filter(supplier__isnull=False)
        .values("supplier__name")
        .annotate(
            total_value=Sum(F("price") * F("quantity")),
            total_parts=Count("id")
        )
        .order_by("-total_value")
    )

    context = {
        "suppliers": suppliers
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/supplier_reports/top_suppliers_by_value_pdf.html",
            context,
            "top-suppliers-by-value.pdf"
        )

    return render(request, "reports/supplier_reports/top_suppliers_by_value.html", context)

@login_required
def low_stock_by_supplier(request):
    LOW_STOCK_THRESHOLD = 5  # 🔹 configurable threshold

    low_stock_parts = (
        SparePart.objects
        .filter(supplier__isnull=False, quantity__lte=LOW_STOCK_THRESHOLD)
        .select_related("supplier", "category")
        .order_by("supplier__name", "name")
    )

    # Group parts by supplier
    grouped = {}
    for part in low_stock_parts:
        supplier = part.supplier.name
        grouped.setdefault(supplier, []).append(part)

    context = {
        "grouped_parts": grouped,
        "threshold": LOW_STOCK_THRESHOLD
    }

    if request.GET.get("format") == "pdf":
        return render_pdf_view(
            "reports/supplier_reports/low_stock_by_supplier_pdf.html",
            context,
            "low-stock-by-supplier.pdf"
        )

    return render(request, "reports/supplier_reports/low_stock_by_supplier.html", context)

@login_required
def reports_overview(request):
    # === Stats ===

    # Total invoice revenue
    total_revenue = Invoice.objects.aggregate(total=Sum("amount"))["total"] or 0

    # Unpaid invoices
    unpaid_total = Invoice.objects.filter(paid=False).aggregate(total=Sum("amount"))["total"] or 0
    unpaid_count = Invoice.objects.filter(paid=False).count()

    # Repairs
    completed_repairs = RepairRecord.objects.filter(status="Completed")
    repair_count = completed_repairs.count()

    avg_repair_time = completed_repairs.exclude(date_out__isnull=True).annotate(
        duration=F("date_out") - F("date_in")
    ).aggregate(
        total_duration=Sum(F("duration"))
    )["total_duration"]

    avg_hours = None
    if avg_repair_time:
        avg_hours = round(avg_repair_time.total_seconds() / 3600 / repair_count, 1)

    # Top customer
    top_customer = (
        Invoice.objects.values("customer__name")
        .annotate(total_spent=Sum("amount"))
        .order_by("-total_spent")
        .first()
    )

    # Top mechanic
    top_mechanic = (
        RepairRecord.objects.filter(status="Completed", mechanic__isnull=False)
        .values("mechanic__name")
        .annotate(total_earned=Sum("cost_of_service"))
        .order_by("-total_earned")
        .first()
    )

    # Inventory stats
    inventory_value = SparePart.objects.aggregate(
        total=Sum(F("quantity") * F("price"))
    )["total"] or 0

    low_stock_count = SparePart.objects.filter(quantity__lte=5).count()

    # === Chart Data ===

    six_months_ago = now() - timedelta(days=180)

    # Invoice revenue by month
    invoice_months = (
        Invoice.objects
        .filter(date_issued__gte=six_months_ago)
        .annotate(month=TruncMonth("date_issued"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )
    chart_invoice_labels = [i["month"].strftime("%b %Y") for i in invoice_months]
    chart_invoice_values = [float(i["total"]) for i in invoice_months]

    # Repairs by month
    repair_months = (
        RepairRecord.objects
        .filter(date_in__gte=six_months_ago)
        .annotate(month=TruncMonth("date_in"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    chart_repair_labels = [r["month"].strftime("%b %Y") for r in repair_months]
    chart_repair_counts = [r["count"] for r in repair_months]

    # Payment method pie
    payment_pie = (
        Invoice.objects
        .values("payment_method")
        .annotate(total=Count("id"))
    )
    chart_payment_labels = [p["payment_method"] for p in payment_pie]
    chart_payment_values = [p["total"] for p in payment_pie]

    #PROFIT STATS
    monthly_profit_data = calculate_profit_by_month()
    chart_profit_labels = [p["month"] for p in monthly_profit_data]
    chart_profit_values = [float(p["profit"]) for p in monthly_profit_data]
    total_profit = calculate_total_profit()

    # === Context ===
    context = {
        "total_revenue": total_revenue,
        "unpaid_total": unpaid_total,
        "unpaid_count": unpaid_count,
        "repair_count": repair_count,
        "avg_repair_time": avg_hours,
        "top_customer": top_customer,
        "top_mechanic": top_mechanic,
        "inventory_value": inventory_value,
        "low_stock_count": low_stock_count,
        "chart_invoice_labels": chart_invoice_labels,
        "chart_invoice_values": chart_invoice_values,
        "chart_repair_labels": chart_repair_labels,
        "chart_repair_counts": chart_repair_counts,
        "chart_payment_labels": chart_payment_labels,
        "chart_payment_values": chart_payment_values,

        "chart_profit_labels": chart_profit_labels,
        "chart_profit_values": chart_profit_values,
        "total_profit": float(total_profit),

    }

    return render(request, "reports/reports_overview.html", context)
