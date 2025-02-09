from django.core.management.base import BaseCommand
from website.scheduler import scheduler

class Command(BaseCommand):
    def handle(self, *args, **options):
        if scheduler.running:
            scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS('Scheduler stopped'))
        else:
            self.stdout.write(self.style.WARNING('Scheduler is not running'))
