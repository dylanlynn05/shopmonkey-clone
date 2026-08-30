from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views


class PublicTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]


router = DefaultRouter()
router.register("customers", views.CustomerViewSet, basename="customer")
router.register("vehicles", views.VehicleViewSet, basename="vehicle")
router.register("technicians", views.TechnicianViewSet, basename="technician")
router.register("work-orders", views.WorkOrderViewSet, basename="workorder")
router.register("service-items", views.ServiceItemViewSet, basename="serviceitem")
router.register("estimates", views.EstimateViewSet, basename="estimate")
router.register("invoices", views.InvoiceViewSet, basename="invoice")

urlpatterns = [
    path("auth/token/", PublicTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]
