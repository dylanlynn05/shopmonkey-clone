from rest_framework import serializers
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


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "notes",
            "created_at",
            "updated_at",
        ]


class VehicleSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "customer",
            "customer_name",
            "year",
            "make",
            "model",
            "vin",
            "license_plate",
            "color",
            "mileage",
            "notes",
            "created_at",
            "updated_at",
        ]

    def get_customer_name(self, obj):
        return str(obj.customer)


class TechnicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technician
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "date_started",
            "level",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ServiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceItem
        fields = [
            "id",
            "name",
            "type",
            "description",
            "default_price",
            "default_quantity",
            "is_active",
            "created_at",
            "updated_at",
        ]


class LineItemSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    class Meta:
        model = LineItem
        fields = [
            "id",
            "service_item",
            "line_type",
            "description",
            "quantity",
            "unit_price",
            "total",
            "sort_order",
        ]

    def get_total(self, obj):
        return obj.total


class EstimateSerializer(serializers.ModelSerializer):
    line_items = LineItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Estimate
        fields = [
            "id",
            "work_order",
            "version",
            "notes",
            "approved_at",
            "line_items",
            "total",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["version"]
        # version is assigned server-side in create_next_estimate; the DB unique constraint still applies.
        validators = []


class WorkOrderSerializer(serializers.ModelSerializer):
    vehicle_detail = VehicleSerializer(source="vehicle", read_only=True)
    technician_name = serializers.SerializerMethodField()
    total_labor = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    estimates = EstimateSerializer(many=True, read_only=True)

    class Meta:
        model = WorkOrder
        fields = [
            "id",
            "vehicle",
            "vehicle_detail",
            "assigned_technician",
            "technician_name",
            "status",
            "priority",
            "description",
            "customer_notes",
            "internal_notes",
            "rate",
            "estimated_time_hours",
            "total_labor",
            "mileage_in",
            "scheduled_date",
            "completed_at",
            "estimates",
            "created_at",
            "updated_at",
        ]

    def get_technician_name(self, obj):
        return str(obj.assigned_technician) if obj.assigned_technician else None


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    class Meta:
        model = InvoiceLineItem
        fields = [
            "id",
            "line_type",
            "description",
            "quantity",
            "unit_price",
            "total",
            "sort_order",
        ]

    def get_total(self, obj):
        return obj.total


class InvoiceSerializer(serializers.ModelSerializer):
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    work_order_detail = WorkOrderSerializer(source="work_order", read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "work_order",
            "work_order_detail",
            "estimate",
            "status",
            "due_date",
            "paid_at",
            "notes",
            "line_items",
            "total",
            "created_at",
            "updated_at",
        ]
