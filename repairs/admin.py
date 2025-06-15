from django.contrib import admin
from .models import RepairRecord, RepairPart, Motorcycle, MotorcycleModel

class RepairPartInline(admin.TabularInline):
    model = RepairPart
    extra = 0

@admin.register(RepairRecord)
class RepairRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "motorcycle", "mechanic", "status", "date_in")
    list_filter = ("status", "date_in", "mechanic")
    search_fields = ("customer__name", "motorcycle__license_plate")
    inlines = [RepairPartInline]

@admin.register(Motorcycle)
class MotorcycleAdmin(admin.ModelAdmin):
    list_display = ("model", "license_plate", "customer", "year")
    search_fields = ("license_plate", "customer__name")
    list_filter = ("model",)

@admin.register(MotorcycleModel)
class MotorcycleModelAdmin(admin.ModelAdmin):
    list_display = ("name", "manufacturer")
