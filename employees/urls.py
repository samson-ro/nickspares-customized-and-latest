from django.urls import path
from . import views

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('add/', views.add_employee, name='add_employee'),
    path('<int:pk>/edit/', views.edit_employee, name='edit_employee'),
    path('<int:pk>/delete/', views.delete_employee, name='delete_employee'),
    path('<int:pk>/', views.employee_detail, name='employee_detail'),
]
