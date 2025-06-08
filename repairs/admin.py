from django.contrib import admin
from .models import RepairRecord, RepairPart

admin.site.register(RepairRecord)
admin.site.register(RepairPart)
