from django.db import models

class SparePart(models.Model):
    name = models.CharField(max_length=100)
    part_number = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=100, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name