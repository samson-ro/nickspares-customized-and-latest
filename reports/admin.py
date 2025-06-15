# reports/admin.py
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from .models import AdminReport

@admin.register(AdminReport)
class ReportsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False
    def has_view_permission(self, request, obj=None): return True

    def changelist_view(self, request, extra_context=None):
        context = dict(
            self.admin_site.each_context(request),
            title="📊 Reports Dashboard",
        )
        return TemplateResponse(request, "admin/reports_dashboard.html", context)
