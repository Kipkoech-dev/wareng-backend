from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusViewSet, BookingViewSet, mpesa_callback

router = DefaultRouter()
router.register('buses', BusViewSet)
router.register('bookings', BookingViewSet)

urlpatterns = [
    path('bookings/mpesa-callback/', mpesa_callback),
    path('', include(router.urls)),
]
