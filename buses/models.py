from django.db import models

class Bus(models.Model):
    bus_number = models.CharField(max_length=20, unique=True)
    bus_name = models.CharField(max_length=100)
    source = models.CharField(max_length=100) # from - eg Nairobi
    destination = models.CharField(max_length=100) # to - eg Mombasa
    total_seats = models.IntegerField(default=60)
    available_seats = models.IntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bus_name} - {self.source} to {self.destination}"

class Booking(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bookings')
    passenger_name = models.CharField(max_length=100)
    passenger_phone = models.CharField(max_length=20)
    seats_booked = models.IntegerField(default=1)
    booking_date = models.DateTimeField(auto_now_add=True)
    booking_time = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.passenger_name} - {self.passenger_phone}"




