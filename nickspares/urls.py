"""
URL configuration for nickspares project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import CustomLoginView, reports_overview, register 
from core.views import CustomLogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),    
    path('logout/', CustomLogoutView.as_view(), name='logout'),    
    path('register/', register, name='register'),

    path('', reports_overview, name='dashboard'),
    path('admin/', admin.site.urls), 

    path('customers/', include('customers.urls')),
    path('repairs/', include('repairs.urls')),
    path('inventory/', include('inventory.urls')),
    path('employees/', include('employees.urls')),
    path('billing/', include('billing.urls')),  
    path('reports/', include('reports.urls')),
 
]
