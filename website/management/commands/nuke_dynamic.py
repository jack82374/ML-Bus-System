from django.core.management.base import BaseCommand
from website.models import TripUpdate, VehiclePosition, StopUpdate, ArchiveTripUpdate, ArchiveVehiclePosition, ArchiveStopUpdate

class Command(BaseCommand):

    def handle(self, *args, **options):
        models_to_delete = [TripUpdate, VehiclePosition, StopUpdate, ArchiveTripUpdate, \
                            ArchiveVehiclePosition, ArchiveStopUpdate] 
        for model in models_to_delete:
            deleted_count, _ = model.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} {model.__name__} objects'))