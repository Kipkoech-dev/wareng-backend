from rest_framework.decorators import api_view
from rest_framework.response import Response
from .mpesa import send_stk_push
from rest_framework import viewsets
import base64
import os
import requests
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Bus, Booking
from .serializers import BusSerializer, BookingSerializer

def get_mpesa_token():
    key = os.environ.get("MPESA_CONSUMER_KEY")
    secret = os.environ.get("MPESA_CONSUMER_SECRET")
    env = os.environ.get("MPESA_ENV", "sandbox")
    base = "https://sandbox.safaricom.co.ke" if env == "sandbox" else "https://api.safaricom.co.ke"
    r = requests.get(f"{base}/oauth/v1/generate?grant_type=client_credentials", auth=(key, secret), timeout=30)
    r.raise_for_status()
    return r.json()["access_token"], base

\
\

lass BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by('-id')
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        booking = serializer.save()
        bus = booking.bus
        bus.available_seats = max(0, bus.available_seats - booking.seats_booked)
        bus.save()

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def pay(self, request, pk=None):
        booking = self.get_object()
        phone = request.data.get("phone") or booking.passenger_phone
        # Normalize to 254...
        phone = str(phone).strip().replace(" ", "").replace("-", "")
        if phone.startswith("0"):
            phone = "254" + phone[1:]
        elif phone.startswith("+"):
            phone = phone[1:]

        amount = int(booking.total_amount)
        shortcode = os.environ.get("MPESA_SHORTCODE", "174379")
        passkey = os.environ.get("MPESA_PASSKEY", "")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()

        try:
            token, base = get_mpesa_token()
        except Exception as e:
            return Response({"error": f"Token failed: {str(e)}"}, status=500)

        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": shortcode,
            "PhoneNumber": phone,
            "CallBackURL": "https://wareng-backend.onrender.com/api/bookings/mpesa-callback/",
            "AccountReference": f"WARENG-{booking.id}",
            "TransactionDesc": f"Wareng booking #{booking.id}",
        }
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        r = requests.post(f"{base}/mpesa/stkpush/v1/processrequest", json=payload, headers=headers, timeout=30)
        data = r.json()
        if r.status_code == 200 and data.get("ResponseCode") == "0":
            booking.checkout_request_id = data.get("CheckoutRequestID")
            booking.save()
            return Response({"message": "STK push sent", "checkout_id": data.get("CheckoutRequestID"), "data": data})
        return Response({"error": "STK push failed", "data": data}, status=400)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def mpesa_callback(request):
    print("MPESA CALLBACK:", request.data)
    try:
        data = request.data
        stk = data.get("Body", {}).get("stkCallback", {})
        result_code = stk.get("ResultCode")
        checkout_id = stk.get("CheckoutRequestID")
        # AccountReference was WARENG-<id>, but we find booking by checkout_id first
        # fallback: try to get booking id from MerchantRequestID? use checkout_id stored in pay()
        booking = None
        if checkout_id:
            booking = Booking.objects.filter(checkout_request_id=checkout_id).first()
        if not booking:
            # Last resort: try to parse from ResultDesc / metadata - skip
            print("Callback: booking not found for", checkout_id)
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

        if result_code == 0:
            # Success - get receipt
            receipt = ""
            items = stk.get("CallbackMetadata", {}).get("Item", [])
            for item in items:
                if item.get("Name") == "MpesaReceiptNumber":
                    receipt = item.get("Value")
            booking.payment_status = "PAID"
            booking.mpesa_receipt = receipt
            booking.save()
            print(f"Booking {booking.id} marked PAID, receipt {receipt}")
        else:
            booking.payment_status = "FAILED"
            booking.save()
            print(f"Booking {booking.id} marked FAILED, code {result_code}")
    except Exception as e:
        print("Callback error:", e)
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
