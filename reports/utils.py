import os
from weasyprint import HTML, CSS
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
import datetime

from decimal import Decimal
from django.db.models import Sum
from billing.models import Invoice, PurchasedPart
from django.db.models.functions import TruncMonth

def render_pdf_view(template_path, context, filename="report.pdf"):
    html_string = render_to_string(template_path, context)
    html = HTML(string=html_string)
    css_path = os.path.join(settings.BASE_DIR, 'static', 'css', 'pdf.css')
    css = CSS(filename=css_path)
    pdf_file = html.write_pdf(stylesheets=[css])

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def parse_date_range(request):
    from_date = request.GET.get("from")
    to_date = request.GET.get("to")
    
    try:
        from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date() if from_date else None
        to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date() if to_date else None
    except ValueError:
        from_date = to_date = None

    return from_date, to_date


def calculate_profit_by_month():
    from collections import defaultdict

    monthly_profit = defaultdict(Decimal)

    invoices = Invoice.objects.all().prefetch_related("purchased_parts__part")
    for invoice in invoices:
        month = invoice.date_issued.replace(day=1)
        revenue = invoice.amount
        cost = sum([
            p.quantity * (p.part.procurement_cost or Decimal("0"))
            for p in invoice.purchased_parts.all()
        ])
        profit = revenue - cost
        monthly_profit[month] += profit

    return [
        {"month": m.strftime("%b %Y"), "profit": float(p)}
        for m, p in sorted(monthly_profit.items())
    ]


def calculate_total_profit():
    total_profit = Decimal("0")

    invoices = Invoice.objects.all().prefetch_related("purchased_parts__part")
    for invoice in invoices:
        revenue = invoice.amount
        part_cost = sum([
            p.quantity * (p.part.procurement_cost or Decimal("0"))
            for p in invoice.purchased_parts.all()
        ])
        profit = revenue - part_cost
        total_profit += profit

    return total_profit