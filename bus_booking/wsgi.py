"""
WSGI config for bus_booking project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bus_booking.settings')

application = get_wsgi_application()

# AUTO-CREATE ADMIN - FREE TRICK, DELETE AFTER LOGIN
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username='wareng').exists():
        User.objects.create_superuser('wareng', 'wareng@gmail.com', 'Wareng1234')
        print("Superuser wareng created")
except Exception as e:
    print(f"Auto-create admin skipped: {e}")