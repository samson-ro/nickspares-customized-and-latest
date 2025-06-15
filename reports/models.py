# core/admin.py or reports/admin.py
from django.contrib import admin
from django.template.response import TemplateResponse

from django.db import models

class AdminReport(models.Model):
    class Meta:
        managed = False  # No DB table will be created
        verbose_name = "📊 Reports Dashboard"
        verbose_name_plural = "📊 Reports Dashboard"
