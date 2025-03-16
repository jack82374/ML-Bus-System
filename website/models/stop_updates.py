# models.py
from django.db import models
from website.models import Stops, Trips

class StopUpdate(models.Model):
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE)
    stop_sequence = models.IntegerField()
    arrival_time = models.IntegerField(null=True, blank=True)
    arrival_uncertainty = models.IntegerField(null=True, blank=True)
    arrival_delay = models.IntegerField(null=True, blank=True)
    departure_delay = models.IntegerField(null=True, blank=True)
    stop = models.ForeignKey(Stops, on_delete=models.CASCADE)
    schedule_relationship = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.stop_sequence} of {self.trip}."