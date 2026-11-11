from django.db import models
from django.contrib.auth.models import User
from datetime import date
from decimal import Decimal

class Customer(models.Model):
    """Customer (vehicle owner) for the repair shop."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class Vehicle(models.Model):
    """Vehicle linked to a customer."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="vehicles")
    year = models.PositiveIntegerField()
    make = models.CharField(max_length=80)
    model = models.CharField(max_length=80)
    vin = models.CharField(max_length=17, blank=True)
    license_plate = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=40, blank=True)
    mileage = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"


class Technician(models.Model):
    """Shop technician (can be linked to User for login)."""

    class Level(models.TextChoices):
        A = "A", "A Tech"
        B = "B", "B Tech"
        C = "C", "C Tech"

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="technician")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_started = models.DateField(default=date.today)
    level = models.CharField(max_length=1, choices=Level.choices, default=Level.C)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class WorkOrder(models.Model):
    """Repair job / work order."""
    class Status(models.TextChoices):
        WAITING_CUSTOMER_APPROVAL = "waiting_customer_approval", "Waiting on customer approval"
        WAITING_PARTS = "waiting_parts", "Waiting on parts"
        IN_PROGRESS = "in_progress", "In progress"
        READY_PICKUP = "ready_pickup", "Ready for pickup"
        COMPLETED = "completed", "Completed"

    class Priority(models.IntegerChoices):
        LOW = 1, "Low"
        NORMAL = 2, "Normal"
        HIGH = 3, "High"
        URGENT = 4, "Urgent"

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="work_orders")
    assigned_technician = models.ForeignKey(
        Technician, on_delete=models.SET_NULL, null=True, blank=True, related_name="work_orders"
    )
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.WAITING_CUSTOMER_APPROVAL)
    priority = models.PositiveSmallIntegerField(
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True,
    )
    description = models.TextField(blank=True)
    customer_notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_time_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    mileage_in = models.PositiveIntegerField(null=True, blank=True)
    scheduled_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "-created_at"]

    def __str__(self):
        return f"WO #{self.pk} – {self.vehicle}"

    @property
    def total_labor(self):
        return (self.rate or Decimal("0")) * (self.estimated_time_hours or Decimal("0"))


class ServiceItem(models.Model):
    """Canned service or part (labor/parts catalog)."""
    class Type(models.TextChoices):
        LABOR = "labor", "Labor"
        PART = "part", "Part"

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=Type.choices)
    description = models.TextField(blank=True)
    default_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    default_quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["type", "name"]

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"


class Estimate(models.Model):
    """Estimate for a work order (can have multiple revisions)."""
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="estimates")
    version = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["work_order", "version"]]

    def __str__(self):
        return f"Estimate #{self.pk} (WO #{self.work_order_id}, v{self.version})"

    @property
    def total(self):
        return sum((item.total for item in self.line_items.all()), Decimal("0"))


class LineItem(models.Model):
    """Single line on an estimate or invoice (labor or part)."""
    class LineType(models.TextChoices):
        LABOR = "labor", "Labor"
        PART = "part", "Part"

    estimate = models.ForeignKey(
        Estimate, on_delete=models.CASCADE, related_name="line_items", null=True, blank=True
    )
    service_item = models.ForeignKey(
        ServiceItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="line_items"
    )
    line_type = models.CharField(max_length=10, choices=LineType.choices)
    description = models.CharField(max_length=300)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "pk"]

    @property
    def total(self):
        return self.quantity * self.unit_price


class Invoice(models.Model):
    """Invoice for a completed (or partial) work order."""
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        PAID = "paid", "Paid"
        PARTIAL = "partial", "Partially Paid"
        OVERDUE = "overdue", "Overdue"

    work_order = models.OneToOneField(WorkOrder, on_delete=models.CASCADE, related_name="invoice")
    estimate = models.ForeignKey(
        Estimate, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    due_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invoice #{self.pk} (WO #{self.work_order_id})"

    @property
    def total(self):
        return sum((item.total for item in self.line_items.all()), Decimal("0"))


class InvoiceLineItem(models.Model):
    """Line item on an invoice (snapshot of labor/parts charged)."""
    class LineType(models.TextChoices):
        LABOR = "labor", "Labor"
        PART = "part", "Part"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="line_items")
    line_type = models.CharField(max_length=10, choices=LineType.choices)
    description = models.CharField(max_length=300)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "pk"]

    @property
    def total(self):
        return self.quantity * self.unit_price
