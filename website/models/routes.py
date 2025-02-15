from django.db import models

from website.models import Agency

class Routes(models.Model):
    route_id = models.CharField(max_length=255, primary_key=True)
    agency = models.ForeignKey(Agency, on_delete=models.RESTRICT)
    route_short_name = models.CharField(max_length=12)
    route_long_name = models.CharField(max_length=255)
    route_desc = models.CharField(max_length=512)
    route_type = models.SmallIntegerField()
    route_url = models.CharField(max_length=255)
    route_color = models.CharField(max_length=6)
    route_text_color = models.CharField(max_length=6)

    def __str__(self):
        return self.route_short_name