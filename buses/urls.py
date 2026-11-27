from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusViewSet, BookingViewSet, initiate_payment, mpesa_callback

router = DefaultRouter()
router.register(r'buses', BusViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('bookings/<int:booking_id>/pay/', initiate_payment),
    path('mpesa/callback/', mpesa_callback),
]