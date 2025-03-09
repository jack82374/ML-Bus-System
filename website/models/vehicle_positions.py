# models.py
from django.db import models
from website.models import Routes, Trips

class VehiclePosition(models.Model):
    #id = models.CharField(max_length=255, primary_key=True)
    trip = models.OneToOneField(Trips, on_delete=models.CASCADE, primary_key=True)
    start_time = models.IntegerField()
    start_date = models.IntegerField()
    schedule_relationship = models.CharField(max_length=255)
    route = models.ForeignKey(Routes, on_delete=models.CASCADE)
    direction_id = models.SmallIntegerField() # 208: 0 is towards hospice, 1 is towards Mayfield. 205: 0 is towards MTU, 1 is towards the station
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField()
    vehicle_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.trip.trip_id} vehicle {self.vehicle_id} at location {self.longitude}, {self.latitude}."