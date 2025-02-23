# models.py
from django.db import models
from website.models import Stops, Trips

class ArchiveStopUpdate(models.Model):
    trip = models.ForeignKey(Trips, null=True, blank=True, on_delete=models.SET_NULL)
    stop_sequence = models.IntegerField()
    arrival_time = models.IntegerField(null=True, blank=True)
    arrival_uncertainty = models.IntegerField(null=True, blank=True)
    arrival_delay = models.IntegerField(null=True, blank=True)
    departure_delay = models.IntegerField(null=True, blank=True)
    stop_id = models.ForeignKey(Stops, null=True, blank=True, on_delete=models.SET_NULL)
    schedule_relationship = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.stop_sequence} at {self.arrival_time}."