from rest_framework import serializers
from .models import Bus, Booking

class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    bus_details = BusSerializer(source='bus', read_only=True)
    class Meta:
        model = Booking
        fields = '__all__'

