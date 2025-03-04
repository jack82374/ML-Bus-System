from django.core.management.base import BaseCommand
from website.models import Routes, Stops, Trips, StopTimes, Calendar, CalendarDates, \
    Agency, Shapes, FeedInfo, GTFSDataInfo, SiteSettings, TripUpdate, VehiclePosition, StopUpdate, ArchiveTripUpdate, ArchiveVehiclePosition, ArchiveStopUpdate

class Command(BaseCommand):

    def handle(self, *args, **options):
        models_to_delete = [StopTimes, Trips, Routes, CalendarDates, Calendar, Stops, Agency, Shapes,\
                                            TripUpdate, VehiclePosition, StopUpdate, ArchiveTripUpdate, ArchiveVehiclePosition, ArchiveStopUpdate, FeedInfo,\
                                                GTFSDataInfo, SiteSettings ] 
        for model in models_to_delete:
            deleted_count, _ = model.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} {model.__name__} objects'))