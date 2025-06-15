from django.contrib import admin
from .models import Invoice, InvoiceItem, PurchasedPart

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0

class PurchasedPartInline(admin.TabularInline):
    model = PurchasedPart
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "amount", "paid", "payment_method", "date_issued")
    search_fields = ("customer__name",)
    list_filter = ("paid", "payment_method", "date_issued")
    inlines = [InvoiceItemInline, PurchasedPartInline]
