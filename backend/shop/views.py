from django.db import transaction
from django.db.models import Count, Max
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
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
from .serializers import (
    CustomerSerializer,
    VehicleSerializer,
    TechnicianSerializer,
    WorkOrderSerializer,
    ServiceItemSerializer,
    EstimateSerializer,
    LineItemSerializer,
    InvoiceSerializer,
    InvoiceLineItemSerializer,
)


def create_next_estimate(work_order, **fields):
    """Create the next estimate revision for a work order (v1, v2, ...)."""
    with transaction.atomic():
        # Lock the work order row so two concurrent requests can't pick the same version.
        WorkOrder.objects.select_for_update().filter(pk=work_order.pk).first()
        latest = work_order.estimates.aggregate(v=Max("version"))["v"] or 0
        return Estimate.objects.create(work_order=work_order, version=latest + 1, **fields)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    search_fields = ["first_name", "last_name", "email", "phone"]


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.select_related("customer")
    serializer_class = VehicleSerializer
    search_fields = ["make", "model", "vin", "license_plate", "customer__last_name"]

    def get_queryset(self):
        qs = super().get_queryset()
        customer_id = self.request.query_params.get("customer_id")
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        return qs


class TechnicianViewSet(viewsets.ModelViewSet):
    queryset = Technician.objects.filter(is_active=True)
    serializer_class = TechnicianSerializer


class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.select_related("vehicle", "vehicle__customer", "assigned_technician").prefetch_related(
        "estimates", "estimates__line_items"
    )
    serializer_class = WorkOrderSerializer
    search_fields = ["description", "vehicle__make", "vehicle__model", "vehicle__customer__last_name"]

    def get_queryset(self):
        qs = super().get_queryset().order_by("-priority", "-created_at")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Counts for the dashboard, computed in the database instead of from a single page of results."""
        # order_by() clears Meta.ordering, which would otherwise be added to the GROUP BY.
        by_status = {
            row["status"]: row["n"]
            for row in WorkOrder.objects.order_by().values("status").annotate(n=Count("id"))
        }
        open_statuses = [s for s in WorkOrder.Status.values if s != WorkOrder.Status.COMPLETED]
        return Response(
            {
                "work_orders_by_status": {s: by_status.get(s, 0) for s in WorkOrder.Status.values},
                "open_work_orders": sum(by_status.get(s, 0) for s in open_statuses),
                "urgent_open_work_orders": WorkOrder.objects.filter(
                    status__in=open_statuses, priority=WorkOrder.Priority.URGENT
                ).count(),
                "customers": Customer.objects.count(),
                "vehicles": Vehicle.objects.count(),
                "active_technicians": Technician.objects.filter(is_active=True).count(),
            }
        )

    @action(detail=True, methods=["post"])
    def create_estimate(self, request, pk=None):
        work_order = self.get_object()
        estimate = create_next_estimate(work_order)
        serializer = EstimateSerializer(estimate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ServiceItemViewSet(viewsets.ModelViewSet):
    queryset = ServiceItem.objects.filter(is_active=True)
    serializer_class = ServiceItemSerializer
    search_fields = ["name", "description"]


class EstimateViewSet(viewsets.ModelViewSet):
    queryset = Estimate.objects.prefetch_related("line_items")
    serializer_class = EstimateSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        work_order_id = self.request.query_params.get("work_order_id")
        if work_order_id:
            qs = qs.filter(work_order_id=work_order_id)
        return qs

    def perform_create(self, serializer):
        data = dict(serializer.validated_data)
        work_order = data.pop("work_order")
        serializer.instance = create_next_estimate(work_order, **data)


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related(
        "work_order", "work_order__vehicle", "work_order__vehicle__customer", "work_order__assigned_technician"
    ).prefetch_related("line_items", "work_order__estimates", "work_order__estimates__line_items")
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs
