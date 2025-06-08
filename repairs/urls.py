from django.urls import path
from . import views

urlpatterns = [
    path('', views.repair_list, name='repair_list'),
    path('add/', views.add_repair, name='add_repair'),
    path('<int:pk>/', views.repair_detail, name='repair_detail'),
    path('<int:pk>/edit/', views.edit_repair, name='edit_repair'),
    path('<int:pk>/delete/', views.delete_repair, name='delete_repair'),

]
