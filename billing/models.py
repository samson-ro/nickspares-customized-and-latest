from django.db import models
from django.db import models
from customers.models import Customer
from repairs.models import RepairRecord
from inventory.models import SparePart

class Invoice(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('M-Pesa', 'M-Pesa'),
        ('Card', 'Card'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    repair = models.ForeignKey(RepairRecord, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    date_issued = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.name}"
    
class SparePartPurchase(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='purchased_parts')
    part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.part.name}"
