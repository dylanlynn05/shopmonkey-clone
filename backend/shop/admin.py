from django.contrib import admin
from .models import (
    Customer,
    Vehicle,
    Technician,
    WorkOrder,
    ServiceItem,
    Estimate,
    LineItem,
    Invoice,
    InvoiceLineItem,
)


class VehicleInline(admin.TabularInline):
    model = Vehicle
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "phone", "email")
    search_fields = ("first_name", "last_name", "email", "phone")
    inlines = [VehicleInline]


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("year", "make", "model", "vin", "license_plate", "customer")
    list_filter = ("make",)
    search_fields = ("vin", "license_plate", "make", "model")


@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "email", "is_active")


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "priority", "status", "assigned_technician", "scheduled_date", "created_at")
    list_filter = ("status", "priority")
    search_fields = ("vehicle__make", "vehicle__model", "description")
    raw_id_fields = ("vehicle", "assigned_technician")


class LineItemInline(admin.TabularInline):
    model = LineItem
    extra = 0


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ("id", "work_order", "version", "created_at")
    inlines = [LineItemInline]


@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "default_price", "default_quantity", "is_active")
    list_filter = ("type",)


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "work_order", "status", "due_date", "created_at")
    list_filter = ("status",)
    inlines = [InvoiceLineItemInline]
