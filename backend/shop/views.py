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


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    search_fields = ["first_name", "last_name", "email", "phone"]
    filterset_fields = []


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.select_related("customer")
    serializer_class = VehicleSerializer

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

    def get_queryset(self):
        qs = super().get_queryset().order_by("-priority", "-created_at")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    @action(detail=True, methods=["post"])
    def create_estimate(self, request, pk=None):
        work_order = self.get_object()
        estimate = Estimate.objects.create(work_order=work_order)
        serializer = EstimateSerializer(estimate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ServiceItemViewSet(viewsets.ModelViewSet):
    queryset = ServiceItem.objects.filter(is_active=True)
    serializer_class = ServiceItemSerializer


class EstimateViewSet(viewsets.ModelViewSet):
    queryset = Estimate.objects.prefetch_related("line_items")
    serializer_class = EstimateSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        work_order_id = self.request.query_params.get("work_order_id")
        if work_order_id:
            qs = qs.filter(work_order_id=work_order_id)
        return qs


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related("work_order").prefetch_related("line_items")
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs
