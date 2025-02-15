from django.db import models

from website.models import Calendar

class CalendarDates(models.Model):
    service = models.ForeignKey(Calendar, on_delete=models.RESTRICT)
    date = models.IntegerField()
    exception_type = models.SmallIntegerField()

    def __str__(self):
        return self.date