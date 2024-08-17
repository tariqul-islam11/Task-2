# serializers.py
from rest_framework import serializers
from .models import District

class DistrictTemperatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['districts_id', 'name', 'division_id', 'bn_name', 'lat', 'lon']
