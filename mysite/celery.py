"""
Celery configuration for background tasks.
"""
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.development')

app = Celery('olaf_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'cleanup-expired-tokens': {
        'task': 'authentication.tasks.cleanup_expired_tokens',
        'schedule': 3600.0,  # Run every hour
    },
    'optimize-mongodb': {
        'task': 'authentication.tasks.optimize_mongodb',
        'schedule': 86400.0,  # Run daily
    },
    'backup-user-data': {
        'task': 'authentication.tasks.backup_user_data',
        'schedule': 604800.0,  # Run weekly
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
