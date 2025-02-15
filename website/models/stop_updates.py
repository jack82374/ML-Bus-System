# models.py
from django.db import models
from website.models import Stops, TripUpdate

class StopUpdate(models.Model):
    trip_update = models.ForeignKey(TripUpdate, on_delete=models.CASCADE)
    stop_sequence = models.IntegerField()
    arrival_time = models.TimeField()
    arrival_uncertainty = models.IntegerField()
    arrival_delay = models.IntegerField()
    departure_delay = models.IntegerField()
    stop_id = models.ForeignKey(Stops, on_delete=models.CASCADE)
    schedule_relationship = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.stop_sequence} of {self.trip_update}."