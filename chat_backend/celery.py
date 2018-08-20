from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
# from celery.schedules import crontab
# from datetime import datetime, timedelta
# from chat.models import ChatSessionMessage


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_backend.settings')

app = Celery('chat_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# time = 10
# days = 1
#
#
# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # Clean data in every 60 * 60 seconds == 1 hour.
#     sender.add_periodic_task(3600.0, clean.s('hourly_clean'), name='add every 1 hour')
#
#     # Executes every Monday morning at 0:30 a.m.
#     sender.add_periodic_task(
#         crontab(hour=0, minute=30, day_of_week=1),
#         clean.s('Daily Clean'),
#     )
#
#
# @app.task
# def clean(arg):
#     print(arg)
#     ChatSessionMessage.objects.filter(create_date__gte=datetime.now() - timedelta(days=days)).delete()