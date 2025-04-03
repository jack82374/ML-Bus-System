from django.core.management.base import BaseCommand
from website.models import NextDelay

class Command(BaseCommand):

    def handle(self, *args, **options):
        NextDelay.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted delays'))