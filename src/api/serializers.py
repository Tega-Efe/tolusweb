from rest_framework import serializers
from .models import FlowData

class FlowDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowData
        fields = ['id', 'user', 'distributionID', 'sensor_id', 'flowRate', 'volume', 'created']
        read_only_fields = ['created']