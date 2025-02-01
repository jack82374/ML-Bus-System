from django.db import models

'''class UniqueShape(models.Model):  # New model for unique shapes
    shape_id = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.shape_id'''

class Shapes(models.Model):
    #pk = models.CompositePrimaryKey("shape_id", "shape_pt_sequence")
    #unique_shape = models.ForeignKey(UniqueShape, on_delete=models.RESTRICT)
    shape_id = models.CharField(max_length=255)
    shape_pt_lat = models.FloatField()
    shape_pt_lon = models.FloatField()
    shape_pt_sequence = models.IntegerField()
    shape_dist_traveled = models.FloatField()

    class Constraint:
        unique_together = (('shape_id', 'shape_pt_sequence'),)

    def __str__(self):
        return f"{self.shape_id} - {self.shape_pt_sequence}"