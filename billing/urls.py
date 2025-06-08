from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('add/', views.add_invoice, name='add_invoice'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('<int:pk>/edit/', views.edit_invoice, name='edit_invoice'),
    path('<int:pk>/delete/', views.delete_invoice, name='delete_invoice'),
    path('purchase/', views.purchase_spare_parts, name='purchase_parts'),
]
