from django.db import models

class District(models.Model):
    districts_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    division_id = models.CharField(max_length=100, blank=True, null=True)
    bn_name = models.CharField(max_length=100, blank=True, null=True)
    lat = models.FloatField()
    lon = models.FloatField()

    class Meta:
        verbose_name = "District"
        verbose_name_plural = "Districts"

    def __str__(self):
        return self.name
