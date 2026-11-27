from rest_framework.decorators import api_view
from rest_framework.response import Response
from .mpesa import send_stk_push
from rest_framework import viewsets
from .models import Bus, Booking
from .serializers import BusSerializer, BookingSerializer


\
\

lass BusViewSet(viewsets.ModelViewSet):
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

@api_view(['POST'])
def initiate_payment(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    result = send_stk_push(booking.passenger_phone, booking.total_amount, booking.id)
    booking.checkout_request_id = result.get('CheckoutRequestID', '')
    booking.save()
    return Response(result)

@api_view(['POST'])
def mpesa_callback(request):
    data = request.data['Body']['stkCallback']
    result_code = data['ResultCode']
    checkout_id = data['CheckoutRequestID']
    
    try:
        booking = Booking.objects.get(checkout_request_id=checkout_id)
    except Booking.DoesNotExist:
        return Response({"ResultCode": 0, "ResultDesc": "OK"})
    
    if result_code == 0:
        # 0 = PAID - correct PIN
        items = {i['Name']: i.get('Value') for i in data['CallbackMetadata']['Item']}
        booking.payment_status = 'paid'
        booking.mpesa_code = items.get('MpesaReceiptNumber', '')
    else:
        # 1032 = Cancelled, 2001 = Wrong PIN, 1037 = Timeout
        # Anything not 0 = FAILED
        booking.payment_status = 'failed'
        bus = booking.bus
        bus.available_seats += booking.seats_booked
        bus.save()
    
    booking.save()
    return Response({"ResultCode": 0, "ResultDesc": "OK"})



