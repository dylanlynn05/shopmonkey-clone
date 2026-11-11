from decimal import Decimal
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from rest_framework.test import APITestCase

from .models import Customer, Estimate, LineItem, Vehicle, WorkOrder


class ShopAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("tester", password="pw-12345!")
        self.client.force_authenticate(self.user)
        self.customer = Customer.objects.create(first_name="Alicia", last_name="Barnes", phone="704-555-0142")
        self.vehicle = Vehicle.objects.create(customer=self.customer, year=2019, make="Honda", model="Civic")
        self.work_order = WorkOrder.objects.create(
            vehicle=self.vehicle, rate=Decimal("135.00"), estimated_time_hours=Decimal("2.50")
        )


class AuthTests(ShopAPITestCase):
    def test_api_requires_authentication(self):
        self.client.force_authenticate(None)
        response = self.client.get("/api/work-orders/")
        self.assertEqual(response.status_code, 401)

    def test_login_returns_access_and_refresh_tokens(self):
        self.client.force_authenticate(None)
        response = self.client.post("/api/auth/token/", {"username": "tester", "password": "pw-12345!"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        refreshed = self.client.post("/api/auth/token/refresh/", {"refresh": response.data["refresh"]})
        self.assertEqual(refreshed.status_code, 200)
        self.assertIn("access", refreshed.data)


class EstimateVersionTests(ShopAPITestCase):
    def test_create_estimate_action_increments_version(self):
        url = f"/api/work-orders/{self.work_order.id}/create_estimate/"
        first = self.client.post(url)
        second = self.client.post(url)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        self.assertEqual([first.data["version"], second.data["version"]], [1, 2])

    def test_estimate_endpoint_assigns_next_version(self):
        Estimate.objects.create(work_order=self.work_order, version=1)
        response = self.client.post("/api/estimates/", {"work_order": self.work_order.id, "notes": "Revised"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["version"], 2)

    def test_estimate_total_sums_line_items(self):
        estimate = Estimate.objects.create(work_order=self.work_order)
        LineItem.objects.create(estimate=estimate, line_type="labor", description="Brakes", quantity=Decimal("1.5"), unit_price=Decimal("135.00"))
        LineItem.objects.create(estimate=estimate, line_type="part", description="Pads", quantity=Decimal("1"), unit_price=Decimal("64.99"))
        response = self.client.get(f"/api/estimates/{estimate.id}/")
        self.assertEqual(response.data["total"], "267.49")


class WorkOrderTests(ShopAPITestCase):
    def test_total_labor_is_exact_decimal_string(self):
        response = self.client.get(f"/api/work-orders/{self.work_order.id}/")
        self.assertEqual(response.data["total_labor"], "337.50")

    def test_work_orders_sorted_by_priority(self):
        urgent = WorkOrder.objects.create(vehicle=self.vehicle, priority=WorkOrder.Priority.URGENT)
        response = self.client.get("/api/work-orders/")
        self.assertEqual(response.data["results"][0]["id"], urgent.id)

    def test_stats_counts_every_work_order_not_just_first_page(self):
        WorkOrder.objects.bulk_create(
            [WorkOrder(vehicle=self.vehicle, status=WorkOrder.Status.IN_PROGRESS) for _ in range(25)]
        )
        WorkOrder.objects.create(vehicle=self.vehicle, status=WorkOrder.Status.COMPLETED)
        response = self.client.get("/api/work-orders/stats/")
        self.assertEqual(response.status_code, 200)
        by_status = response.data["work_orders_by_status"]
        self.assertEqual(by_status["in_progress"], 25)
        self.assertEqual(by_status["waiting_customer_approval"], 1)
        self.assertEqual(by_status["completed"], 1)
        self.assertEqual(response.data["open_work_orders"], 26)
        self.assertEqual(response.data["customers"], 1)


class SearchTests(ShopAPITestCase):
    def test_customer_search(self):
        Customer.objects.create(first_name="Derek", last_name="Coleman", phone="704-555-0187")
        response = self.client.get("/api/customers/", {"search": "cole"})
        self.assertEqual([c["last_name"] for c in response.data["results"]], ["Coleman"])


class SeedDemoTests(ShopAPITestCase):
    def test_seed_demo_reset_loads_data(self):
        call_command("seed_demo", "--reset", stdout=StringIO())
        self.assertGreater(WorkOrder.objects.count(), 5)
        self.assertEqual(Estimate.objects.filter(version=2).count(), 1)
