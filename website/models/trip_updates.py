# models.py
from django.db import models
from website.models.routes import Routes
from website.models.trips import Trips

class TripUpdate(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE)
    start_time = models.TimeField()
    start_date = models.IntegerField()
    schedule_relationship = models.CharField(max_length=255)
    route = models.ForeignKey(Routes, on_delete=models.CASCADE)
    direction_id = models.SmallIntegerField()
    stop_time_updates = models.JSONField()
    vehicle_id = models.IntegerField()
    timestamp = models.TimeField()

    def __str__(self):
        return f"{self.trip.trip_id} updated at {self.timestamp}."