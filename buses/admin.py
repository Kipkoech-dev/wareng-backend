from django.contrib import admin
from .models import Bus, Booking

admin.site.register(Bus)
admin.site.register(Booking)
admin.site.site_header = "WARENG Admin"
admin.site.site_title = "WARENG Admin Portal"
admin.site.index_title = "Welcome to WARENG - Manage Vehicles & Bookings"