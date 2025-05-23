import os
import signal
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command

# Define the scheduler
scheduler = BackgroundScheduler(timezone=timezone.get_current_timezone())
scheduler.add_jobstore(DjangoJobStore(), "default")

def run_get_gtfs():
    call_command('get_gtfs')

def refresh_static():
    call_command('get_static_gtfs_files')

def retrain_model():
    call_command('mltest')

# Schedule the task
def add_jobs():
    scheduler.add_job(run_get_gtfs, 'interval', minutes=1, id='get_trip_and_location_updates', replace_existing=True)
    static_trigger = CronTrigger(
            year="*", month="*", day="*", hour="1", minute="30", second="0"
        )
    scheduler.add_job(refresh_static, static_trigger, id='refresh_static_gtfs_files', replace_existing=True)
    training_triger = CronTrigger(
            year="*", month="*", day_of_week="thu", hour="1", minute="0", second="0"
        )
    scheduler.add_job(retrain_model, training_triger, id='retrain_ml_model', replace_existing=True)

def start_scheduler():
    add_jobs()
    if os.environ.get('RUN_MAIN') == 'true':
        if not scheduler.running:
            scheduler.start()
            print(f"Scheduler started.")
        else:
            print(f"Scheduler is already running.")