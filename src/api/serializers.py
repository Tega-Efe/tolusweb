from rest_framework import serializers
from .models import FlowData, TokenHistory

class FlowDataSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()
    
    class Meta:
        model = FlowData
        fields = '__all__'
        
    def get_created(self, obj):
        return obj.created.strftime('%d-%m-%Y %H:%M') if obj.created else None

class TokenHistorySerializer(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    
    class Meta:
        model = TokenHistory
        fields = '__all__'
        
    def get_start_date(self, obj):
        return obj.start_date.strftime('%d-%m-%Y %H:%M') if obj.start_date else None
        
    def get_last_updated(self, obj):
        return obj.last_updated.strftime('%d-%m-%Y %H:%M') if obj.last_updated else None
        
    def get_end_date(self, obj):
        return obj.end_date.strftime('%d-%m-%Y %H:%M') if obj.end_date else None