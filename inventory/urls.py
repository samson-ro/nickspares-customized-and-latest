from django.urls import path
from . import views

urlpatterns = [
    path('', views.sparepart_list, name='sparepart_list'),
    path('add/', views.add_sparepart, name='add_sparepart'),
    path('<int:pk>/edit/', views.edit_sparepart, name='edit_sparepart'),
    path('<int:pk>/delete/', views.delete_sparepart, name='delete_sparepart'),
    path('<int:pk>/', views.sparepart_detail, name='sparepart_detail'),
]
