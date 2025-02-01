from django.db import models

class Agency(models.Model):
    agency_id = models.IntegerField(primary_key=True)
    agency_name = models.CharField(max_length=255)
    agency_url = models.CharField(max_length=255)
    agency_timezone = models.CharField(max_length=255)

    def __str__(self):
        return self.agency_name