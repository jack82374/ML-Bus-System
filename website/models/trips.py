from django.db import models

from website.models import Calendar, Routes

class Trips(models.Model):
    route= models.ForeignKey(Routes, on_delete=models.RESTRICT)
    service = models.ForeignKey(Calendar, on_delete=models.RESTRICT)
    trip_id = models.CharField(max_length=255, primary_key=True)
    trip_headsign = models.CharField(max_length=255)
    trip_short_name = models.CharField(max_length=255)
    direction_id = models.BooleanField()
    block_id = models.CharField(max_length=255)
    shape_id = models.CharField(max_length=255)


    def __str__(self):
        return self.trip_short_name