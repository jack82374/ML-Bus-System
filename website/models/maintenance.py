from django.db import models

class SiteSettings(models.Model):
    maintenance_mode = models.BooleanField(default=False)

    def __str__(self):
        return f"Maintenance Mode: {'Enabled' if self.maintenance_mode else 'Disabled'}"