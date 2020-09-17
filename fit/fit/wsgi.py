"""
WSGI config for fit project с помощью него приложение может работать с веб-сервером(Nginx, Apache, и многими другими) по протоколу WSGI.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fit.settings')

application = get_wsgi_application()
