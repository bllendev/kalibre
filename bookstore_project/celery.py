from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore_project.settings')

app = Celery('bookstore_project')

# Use Django's settings for the Celery configuration
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    logger.debug(f'Request: {self.request!r}')
