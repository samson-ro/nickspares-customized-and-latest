from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)  # Mechanic, Cashier, etc.
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    hire_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name