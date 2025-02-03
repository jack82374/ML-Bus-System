from django.db import models

from website.models.stops import Stops
from website.models.trips import Trips

'''class UniqueStop(models.Model):  # New model for unique stop combinations
    id = models.BigAutoField(primary_key=True)
    trip = models.ForeignKey(Trips, on_delete=models.RESTRICT)  # Foreign key to Trip
    stop_sequence = models.IntegerField()

    class Contstraint:
        unique_together = (('trip', 'stop_sequence'),)  # Define unique constraint

    def __str__(self):
        return f"{self.trip.trip_id} - Stop {self.stop_sequence}"'''

class StopTimes(models.Model):
    #pk = models.CompositePrimaryKey("trip_id", "stop_sequence")
    #unique_stop = models.ForeignKey(UniqueStop, on_delete=models.RESTRICT)
    trip = models.ForeignKey(Trips, on_delete=models.RESTRICT)  # Foreign key to Trip
    #arrival_time = models.TimeField()
    arrival_time = models.IntegerField()
    #departure_time = models.TimeField()
    departure_time = models.IntegerField()
    stop = models.ForeignKey(Stops, on_delete=models.RESTRICT)
    stop_sequence = models.IntegerField()
    stop_headsign = models.CharField(max_length=255)
    pickup_type = models.SmallIntegerField()
    drop_off_type = models.SmallIntegerField()
    timepoint = models.BooleanField()
    
    class Contstraint:
        unique_together = (('trip', 'stop_sequence'),)  # Define unique constraint

    def __str__(self):
        return f"Stop {self.stop_sequence} of Trip {self.trip.trip_id}"