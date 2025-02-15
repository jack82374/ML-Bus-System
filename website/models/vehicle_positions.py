# models.py
from django.db import models
from website.models import Routes, Trips

class VehiclePosition(models.Model):
    #id = models.CharField(max_length=255, primary_key=True)
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE)
    start_time = models.IntegerField()
    start_date = models.IntegerField()
    schedule_relationship = models.CharField(max_length=255)
    route = models.ForeignKey(Routes, on_delete=models.CASCADE)
    direction_id = models.SmallIntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField()
    vehicle_id = models.IntegerField(primary_key=True)

    def __str__(self):
        return f"{self.trip.trip_id} vehicle {self.vehicle_id} at location {self.longitude}, {self.latitude}."