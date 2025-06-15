from django.contrib import admin
from .models import SparePart, Supplier, PartCategory

@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "quantity", "price", "supplier", "date_added")
    search_fields = ("name", "part_number")
    list_filter = ("category", "supplier")

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "phone", "email")

@admin.register(PartCategory)
class PartCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
