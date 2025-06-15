from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse

from billing.models import Invoice
from inventory.models import SparePart
from repairs.models import RepairRecord
from .forms import UserRegisterForm
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView
from django.db.models import Sum, Count
from django.db.models import F
from django.db.models.functions import TruncMonth
from django.utils.timezone import now, timedelta


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
    }

    return render(request, "reports/reports_overview.html", context)

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return reverse('admin:index')
        return reverse('dashboard')

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)
    
class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        list(messages.get_messages(request))
        messages.success(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form, 'title': 'Register'})