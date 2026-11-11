from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from shop.models import (
    Customer,
    Estimate,
    Invoice,
    InvoiceLineItem,
    LineItem,
    ServiceItem,
    Technician,
    Vehicle,
    WorkOrder,
)

TECHNICIANS = [
    ("Marcus", "Reed", Technician.Level.A, 9),
    ("Priya", "Shah", Technician.Level.A, 6),
    ("Tom", "Delgado", Technician.Level.B, 3),
    ("Jess", "Nguyen", Technician.Level.C, 1),
]

SERVICE_ITEMS = [
    ("Diagnostic", ServiceItem.Type.LABOR, "135.00", "1"),
    ("Oil change labor", ServiceItem.Type.LABOR, "35.00", "0.5"),
    ("Brake pad replacement (per axle)", ServiceItem.Type.LABOR, "135.00", "1.5"),
    ("Synthetic oil 5W-30 (qt)", ServiceItem.Type.PART, "9.50", "5"),
    ("Oil filter", ServiceItem.Type.PART, "12.99", "1"),
    ("Ceramic brake pads (front)", ServiceItem.Type.PART, "64.99", "1"),
    ("Brake rotor", ServiceItem.Type.PART, "89.99", "2"),
    ("Battery 650 CCA", ServiceItem.Type.PART, "189.00", "1"),
]

# customer, phone, email, vehicles: (year, make, model, plate, mileage)
CUSTOMERS = [
    ("Alicia", "Barnes", "704-555-0142", "alicia.barnes@example.com", [(2019, "Honda", "Civic", "NCK-4821", 61200)]),
    ("Derek", "Coleman", "704-555-0187", "dcoleman@example.com", [(2016, "Ford", "F-150", "TRK-1190", 118400)]),
    ("Maria", "Gonzalez", "980-555-0110", "", [(2021, "Toyota", "RAV4", "RAV-2021", 34800), (2012, "Toyota", "Camry", "CAM-7712", 152300)]),
    ("Kevin", "Patel", "704-555-0199", "kpatel@example.com", [(2018, "Subaru", "Outback", "SUB-3381", 88900)]),
    ("Sarah", "Kim", "828-555-0123", "sarah.kim@example.com", [(2020, "Tesla", "Model 3", "EVS-0420", 41000)]),
    ("James", "Walker", "704-555-0164", "", [(2015, "Chevrolet", "Silverado", "CHV-5150", 134700)]),
    ("Nina", "Brooks", "980-555-0175", "nina.b@example.com", [(2017, "Jeep", "Wrangler", "JEP-8812", 97300)]),
    ("Omar", "Haddad", "704-555-0131", "ohaddad@example.com", [(2022, "Hyundai", "Elantra", "HYU-2290", 18200)]),
]

# vehicle index, tech index (None = TBD), status, priority, description, rate, hours, days from today
WORK_ORDERS = [
    (0, 0, WorkOrder.Status.IN_PROGRESS, WorkOrder.Priority.URGENT, "Grinding noise when braking – replace front pads and rotors", "135", "2.5", 0),
    (1, 1, WorkOrder.Status.WAITING_PARTS, WorkOrder.Priority.HIGH, "Check engine light – P0420 catalytic converter efficiency", "135", "3", 1),
    (2, None, WorkOrder.Status.WAITING_CUSTOMER_APPROVAL, WorkOrder.Priority.NORMAL, "60k mile service – oil, filters, tire rotation", "120", "1.5", 2),
    (3, 2, WorkOrder.Status.IN_PROGRESS, WorkOrder.Priority.NORMAL, "Oil change and multi-point inspection", "120", "0.75", 0),
    (4, 0, WorkOrder.Status.READY_PICKUP, WorkOrder.Priority.HIGH, "Diagnose intermittent no-start", "135", "1", -1),
    (5, 3, WorkOrder.Status.COMPLETED, WorkOrder.Priority.NORMAL, "Battery replacement", "120", "0.5", -3),
    (6, 1, WorkOrder.Status.WAITING_CUSTOMER_APPROVAL, WorkOrder.Priority.URGENT, "Coolant leak – overheating on highway", "135", "2", 0),
    (7, 2, WorkOrder.Status.COMPLETED, WorkOrder.Priority.LOW, "Replace wiper blades and cabin air filter", "120", "0.5", -5),
    (8, None, WorkOrder.Status.WAITING_CUSTOMER_APPROVAL, WorkOrder.Priority.LOW, "Alignment check – pulls to the right", "120", "1", 3),
]


class Command(BaseCommand):
    help = "Load realistic demo data (customers, vehicles, technicians, work orders, estimates, invoices)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing shop data before seeding.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            for model in (InvoiceLineItem, Invoice, LineItem, Estimate, WorkOrder, Vehicle, Customer, ServiceItem, Technician):
                model.objects.all().delete()
        elif Customer.objects.exists():
            self.stdout.write(self.style.WARNING("Data already exists. Re-run with --reset to replace it."))
            return

        today = date.today()
        techs = [
            Technician.objects.create(
                first_name=first,
                last_name=last,
                email=f"{first.lower()}.{last.lower()}@shop.example.com",
                level=level,
                date_started=today - timedelta(days=365 * years),
            )
            for first, last, level, years in TECHNICIANS
        ]

        catalog = {
            name: ServiceItem.objects.create(
                name=name, type=kind, default_price=Decimal(price), default_quantity=Decimal(qty)
            )
            for name, kind, price, qty in SERVICE_ITEMS
        }

        vehicles = []
        for first, last, phone, email, cars in CUSTOMERS:
            customer = Customer.objects.create(first_name=first, last_name=last, phone=phone, email=email)
            for year, make, model, plate, mileage in cars:
                vehicles.append(
                    Vehicle.objects.create(
                        customer=customer, year=year, make=make, model=model, license_plate=plate, mileage=mileage
                    )
                )

        work_orders = []
        for v_idx, t_idx, wo_status, priority, desc, rate, hours, offset in WORK_ORDERS:
            vehicle = vehicles[v_idx]
            work_orders.append(
                WorkOrder.objects.create(
                    vehicle=vehicle,
                    assigned_technician=techs[t_idx] if t_idx is not None else None,
                    status=wo_status,
                    priority=priority,
                    description=desc,
                    rate=Decimal(rate),
                    estimated_time_hours=Decimal(hours),
                    mileage_in=vehicle.mileage,
                    scheduled_date=today + timedelta(days=offset),
                    completed_at=timezone.now() + timedelta(days=offset) if wo_status == WorkOrder.Status.COMPLETED else None,
                )
            )

        def add_lines(estimate, names):
            for i, name in enumerate(names):
                item = catalog[name]
                LineItem.objects.create(
                    estimate=estimate,
                    service_item=item,
                    line_type=item.type,
                    description=item.name,
                    quantity=item.default_quantity,
                    unit_price=item.default_price,
                    sort_order=i,
                )

        brakes = work_orders[0]
        v1 = Estimate.objects.create(work_order=brakes, version=1, notes="Pads only")
        add_lines(v1, ["Brake pad replacement (per axle)", "Ceramic brake pads (front)"])
        v2 = Estimate.objects.create(
            work_order=brakes, version=2, notes="Rotors below spec – pads and rotors", approved_at=timezone.now()
        )
        add_lines(v2, ["Brake pad replacement (per axle)", "Ceramic brake pads (front)", "Brake rotor"])

        service = Estimate.objects.create(work_order=work_orders[2], version=1, notes="Awaiting customer callback")
        add_lines(service, ["Oil change labor", "Synthetic oil 5W-30 (qt)", "Oil filter"])

        oil = Estimate.objects.create(work_order=work_orders[3], version=1, approved_at=timezone.now())
        add_lines(oil, ["Oil change labor", "Synthetic oil 5W-30 (qt)", "Oil filter"])

        battery = Estimate.objects.create(work_order=work_orders[5], version=1, approved_at=timezone.now())
        add_lines(battery, ["Diagnostic", "Battery 650 CCA"])

        for wo, estimate, inv_status, paid in (
            (work_orders[5], battery, Invoice.Status.PAID, True),
            (work_orders[7], None, Invoice.Status.SENT, False),
        ):
            invoice = Invoice.objects.create(
                work_order=wo,
                estimate=estimate,
                status=inv_status,
                due_date=today + timedelta(days=14),
                paid_at=timezone.now() if paid else None,
            )
            if estimate:
                lines = [(li.line_type, li.description, li.quantity, li.unit_price) for li in estimate.line_items.all()]
            else:
                lines = [(LineItem.LineType.LABOR, wo.description, wo.estimated_time_hours, wo.rate)]
            for i, (line_type, desc, qty, price) in enumerate(lines):
                InvoiceLineItem.objects.create(
                    invoice=invoice, line_type=line_type, description=desc, quantity=qty, unit_price=price, sort_order=i
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(techs)} technicians, {Customer.objects.count()} customers, {len(vehicles)} vehicles, "
                f"{len(work_orders)} work orders, {Estimate.objects.count()} estimates, {Invoice.objects.count()} invoices."
            )
        )
