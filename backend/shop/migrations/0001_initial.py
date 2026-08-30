# Generated manually for shop app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('address', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='ServiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('type', models.CharField(choices=[('labor', 'Labor'), ('part', 'Part')], max_length=10)),
                ('description', models.TextField(blank=True)),
                ('default_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('default_quantity', models.DecimalField(decimal_places=2, default=1, max_digits=8)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['type', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Technician',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='technician', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField()),
                ('make', models.CharField(max_length=80)),
                ('model', models.CharField(max_length=80)),
                ('vin', models.CharField(blank=True, max_length=17)),
                ('license_plate', models.CharField(blank=True, max_length=20)),
                ('color', models.CharField(blank=True, max_length=40)),
                ('mileage', models.PositiveIntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to='shop.customer')),
            ],
            options={
                'ordering': ['-updated_at'],
                'unique_together': {('customer', 'vin')},
            },
        ),
        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('waiting_parts', 'Waiting on Parts'), ('ready_pickup', 'Ready for Pickup'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('customer_notes', models.TextField(blank=True)),
                ('internal_notes', models.TextField(blank=True)),
                ('mileage_in', models.PositiveIntegerField(blank=True, null=True)),
                ('scheduled_date', models.DateField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_technician', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='work_orders', to='shop.technician')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_orders', to='shop.vehicle')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Estimate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.PositiveIntegerField(default=1)),
                ('notes', models.TextField(blank=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('work_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estimates', to='shop.workorder')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('work_order', 'version')},
            },
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line_type', models.CharField(choices=[('labor', 'Labor'), ('part', 'Part')], max_length=10)),
                ('description', models.CharField(max_length=300)),
                ('quantity', models.DecimalField(decimal_places=2, default=1, max_digits=8)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('estimate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='line_items', to='shop.estimate')),
                ('service_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='line_items', to='shop.serviceitem')),
            ],
            options={
                'ordering': ['sort_order', 'pk'],
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid'), ('partial', 'Partially Paid'), ('overdue', 'Overdue')], default='draft', max_length=20)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('estimate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoices', to='shop.estimate')),
                ('work_order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='invoice', to='shop.workorder')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='InvoiceLineItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line_type', models.CharField(choices=[('labor', 'Labor'), ('part', 'Part')], max_length=10)),
                ('description', models.CharField(max_length=300)),
                ('quantity', models.DecimalField(decimal_places=2, default=1, max_digits=8)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_items', to='shop.invoice')),
            ],
            options={
                'ordering': ['sort_order', 'pk'],
            },
        ),
    ]
