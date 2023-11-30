"""
WSGI config for bookstore_project project.
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore_project.settings')

application = get_wsgi_application()
application = WhiteNoise(application)