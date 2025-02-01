from django.db import models

class Stops(models.Model):
    stop_id = models.CharField(max_length=255, primary_key=True)
    stop_code = models.IntegerField(null=True, blank=True)
    stop_name = models.CharField(max_length=255)
    stop_desc = models.CharField(max_length=512)
    stop_lat = models.FloatField()
    stop_lon = models.FloatField()
    zone_id = models.IntegerField(null=True, blank=True)
    stop_url = models.CharField(max_length=255)
    location_type = models.SmallIntegerField(null=True, blank=True)
    parent_station = models.CharField(max_length=255)

    def __str__(self):
        return self.stop_name