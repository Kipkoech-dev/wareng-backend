from rest_framework import viewsets
from .models import Bus, Booking
from .serializers import BusSerializer, BookingSerializer


class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        bus = serializer.validated_data['bus']
        seats = serializer.validated_data['seats_booked']

        if bus.available_seats >= seats:
            bus.available_seats = bus.available_seats - seats
            bus.save()
            serializer.save()
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"error": "Not enough seats available!"})



