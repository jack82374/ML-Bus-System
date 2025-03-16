# models.py
from django.db import models
from website.models import Routes, Trips

class TripUpdate(models.Model):
    #id = models.CharField(max_length=255, primary_key=True)
    trip = models.OneToOneField(Trips, on_delete=models.CASCADE, primary_key=True)
    # Having cascade set in all the live (non archive) models should help to limit the max amount of
    # old trip data that can build up
    start_time = models.IntegerField()
    start_date = models.IntegerField()
    schedule_relationship = models.CharField(max_length=255, null=True, blank=True)
    route = models.ForeignKey(Routes, on_delete=models.CASCADE)
    direction_id = models.SmallIntegerField()
    vehicle_id = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField()
    day = models.SmallIntegerField()

    def __str__(self):
        return f"{self.trip.trip_id} updated at {self.timestamp}."