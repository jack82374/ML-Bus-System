from django.db import models

class Calendar(models.Model):
    service_id = models.IntegerField(primary_key=True)
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    sunday = models.BooleanField()
    start_date = models.IntegerField()
    end_date = models.IntegerField()

    def __str__(self):
        return self.service_id