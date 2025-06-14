# Generated by Django 5.2.1 on 2025-05-16 12:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0001_initial'),
        ('employees', '0001_initial'),
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RepairPart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.sparepart')),
            ],
        ),
        migrations.CreateModel(
            name='RepairRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motorcycle_model', models.CharField(max_length=100)),
                ('complaint', models.TextField()),
                ('work_done', models.TextField(blank=True, null=True)),
                ('total_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('date_in', models.DateTimeField()),
                ('date_out', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=10)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.customer')),
                ('mechanic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='employees.employee')),
                ('parts_used', models.ManyToManyField(through='repairs.RepairPart', to='inventory.sparepart')),
            ],
        ),
        migrations.AddField(
            model_name='repairpart',
            name='repair',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repairs.repairrecord'),
        ),
    ]
