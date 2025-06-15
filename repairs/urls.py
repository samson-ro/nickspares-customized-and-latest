from django.urls import path
from . import views

urlpatterns = [
    path('', views.repair_list, name='repair_list'),
    path('add/', views.add_repair, name='add_repair'),
    path('<int:pk>/', views.repair_detail, name='repair_detail'),
    path('<int:pk>/edit/', views.edit_repair, name='edit_repair'),
    path('<int:pk>/delete/', views.delete_repair, name='delete_repair'),

    # New: Motorcycle Models
    path('motorcyclemodels/', views.motorcycle_model_list, name='motorcycle_model_list'),
    path('motorcyclemodels/add/', views.add_motorcycle_model, name='add_motorcycle_model'),
    path('motorcyclemodels/<int:pk>/edit/', views.edit_motorcycle_model, name='edit_motorcycle_model'),
    path('motorcyclemodels/<int:pk>/delete/', views.delete_motorcycle_model, name='delete_motorcycle_model'),

    # New: Motorcycles
    path('motorcycles/', views.motorcycle_list, name='motorcycle_list'),
    path('motorcycles/add/', views.add_motorcycle, name='add_motorcycle'),
    path('motorcycles/<int:pk>/edit/', views.edit_motorcycle, name='edit_motorcycle'),
    path('motorcycles/<int:pk>/delete/', views.delete_motorcycle, name='delete_motorcycle'),
]
