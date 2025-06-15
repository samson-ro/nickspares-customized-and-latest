from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_number", "email", "role", "hire_date")
    search_fields = ("name", "phone_number", "email")
