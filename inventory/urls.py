from django.urls import path
from . import views

urlpatterns = [
    path('', views.sparepart_list, name='sparepart_list'),
    path('add/', views.add_sparepart, name='add_sparepart'),
    path('<int:pk>/edit/', views.edit_sparepart, name='edit_sparepart'),
    path('<int:pk>/delete/', views.delete_sparepart, name='delete_sparepart'),
    path('<int:pk>/', views.sparepart_detail, name='sparepart_detail'),

    # Supplier URLs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/<int:pk>/edit/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/<int:pk>/delete/', views.delete_supplier, name='delete_supplier'),

    # Part Category URLs
    path('partcategory/', views.partcategory_list, name='partcategory_list'),
    path('partcategory/add/', views.add_partcategory, name='add_partcategory'),
    path('partcategory/<int:pk>/edit/', views.edit_partcategory, name='edit_partcategory'),
    path('partcategory/<int:pk>/delete/', views.delete_partcategory, name='delete_partcategory'),
]
