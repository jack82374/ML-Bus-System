from django.db import models

class GTFSDataInfo(models.Model):
    last_modified = models.DateTimeField(null=True, blank=True)  # Store the last modified date