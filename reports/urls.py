from django.urls import path
from . import views

urlpatterns = [
    path('invoices/', views.invoice_report, name='invoice_report'),
    path('invoices/unpaid/', views.unpaid_invoices_report, name='unpaid_invoices_report'),
    path('invoices/summary/', views.payment_summary_report, name='payment_summary_report'),
    path('invoices/customer/', views.customer_invoice_history, name='customer_invoice_history'),
    path('invoices/top-customers/', views.top_customers_report, name='top_customers_report'),
    path('invoices/monthly/', views.monthly_invoice_breakdown, name='monthly_invoice_breakdown'),
    path('invoices/part-sales/', views.part_sales_report, name='part_sales_report'),

    #Repair Reports
    path('repairs/summary/', views.repair_summary_report, name='repair_summary_report'),
    path('repairs/top-models/', views.top_models_report, name='top_models_report'),
    path('repairs/revenue/', views.repair_revenue_report, name='repair_revenue_report'),
    path('repairs/common-issues/', views.most_common_repairs_report, name='most_common_repairs_report'),
    path('repairs/parts-usage/', views.repair_parts_usage_report, name='repair_parts_usage_report'),
    path('repairs/average-time/', views.average_repair_time_report, name='average_repair_time_report'),

    #Inventory Reports
    path("inventory/summary/", views.inventory_summary_report, name="inventory_summary_report"),
    path("inventory/low-stock/", views.low_stock_report, name="low_stock_report"),
    path("inventory/supplier-inventory/", views.supplier_inventory_report, name="supplier_inventory_report"),
    path("inventory/category-inventory/", views.category_inventory_report, name="category_inventory_report"),
    path("inventory/price-list/", views.price_list_report, name="price_list_report"),
    path("inventory/value-over-time/", views.inventory_value_over_time, name="inventory_value_over_time"),

    #Customer Reports
    path("customers/summary/", views.customer_summary_report, name="customer_summary_report"),
    path("customers/top-revenue/", views.top_customers_by_revenue, name="top_customers_by_revenue"),
    path("customers/most-repairs/", views.customers_with_most_repairs, name="customers_with_most_repairs"),
    path("customers/new-over-time/", views.new_customers_over_time, name="new_customers_over_time"),
    path("customers/service-history/", views.customer_service_history, name="customer_service_history"),
   
    #Employee reports
    path("employees/summary/", views.employee_summary_report, name="employee_summary_report"),
    path("employees/repairs-summary/", views.repair_count_by_mechanic, name="repair_count_by_mechanic"),
    path("employees/mechanic-log/", views.mechanic_workload_detail, name="mechanic_workload_detail"),
    path("employees/monthly-output/", views.monthly_repair_output, name="monthly_repair_output"),
    path("employees/top-mechanics/", views.top_performing_mechanics, name="top_performing_mechanics"),

    path("suppliers/summary/", views.supplier_summary_report, name="supplier_summary_report"),
    path("suppliers/parts-supplied/", views.parts_supplied_per_supplier, name="parts_supplied_per_supplier"),
    path("suppliers/top-value/", views.top_suppliers_by_value, name="top_suppliers_by_value"),
    path("suppliers/low-stock/", views.low_stock_by_supplier, name="low_stock_by_supplier"),
    path("overview/", views.reports_overview, name="reports_overview"),

]
