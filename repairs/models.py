from django.db import models
from customers.models import Customer
from employees.models import Employee
from inventory.models import SparePart

class Motorcycle(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='motorcycles')
    model = models.ForeignKey('MotorcycleModel', on_delete=models.SET_NULL, null=True)
    license_plate = models.CharField(max_length=20, unique=True, blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        model_name = self.model.name if self.model else "Unknown Model"
        plate = self.license_plate or "No Plate"
        return f"{model_name} - {plate}"


class MotorcycleModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class RepairRecord(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    mechanic = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    motorcycle = models.ForeignKey( 'repairs.Motorcycle',
                                    on_delete=models.CASCADE,
                                    null=True, 
                                    blank=True 
                                    )
    complaint = models.TextField()
    work_done = models.TextField(blank=True, null=True)
    cost_of_service = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    date_in = models.DateTimeField()
    date_out = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Repair #{self.id} - {self.customer.name}"

class RepairPart(models.Model):
    repair = models.ForeignKey(RepairRecord, on_delete=models.CASCADE)
    part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.part.name} for Repair #{self.repair.id}"
    