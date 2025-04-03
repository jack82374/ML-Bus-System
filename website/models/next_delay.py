from django.db import models
from website.models import Trips

class NextDelay(models.Model):
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE)
    delay = models.IntegerField()

    def __str__(self):
        return self.delay