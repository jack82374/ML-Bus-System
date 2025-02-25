# models.py
from django.db import models
from website.models import Routes, Trips

class ArchiveVehiclePosition(models.Model):
    #id = models.CharField(max_length=255, primary_key=True)
    #trip = models.ForeignKey(Trips, null=True, blank=True, on_delete=models.SET_NULL)
    trip_id = models.CharField(max_length=255)
    start_time = models.IntegerField()
    start_date = models.IntegerField()
    schedule_relationship = models.CharField(max_length=255)
    #route = models.ForeignKey(Routes, null=True, blank=True, on_delete=models.SET_NULL)
    route_id = models.CharField(max_length=255)
    direction_id = models.SmallIntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField()
    vehicle_id = models.IntegerField()

    def __str__(self):
        return f"{self.trip.trip_id} vehicle {self.vehicle_id} was at location {self.longitude}, {self.latitude} at {self.timestamp}."