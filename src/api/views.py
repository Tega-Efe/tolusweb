from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import FlowDataSerializer
from .models import FlowData
from rest_framework.response import Response

from .utils import *

@api_view(['GET'])
def getRoutes(request):
    routes = [
        {
            'Endpoint': '/flow-data/',
            'method': 'GET, POST',
            'body': {
                'flowRate1': 'float',
                'volume1': 'float',
                'flowRate2': 'float',
                'volume2': 'float',
                'flowRate3': 'float',
                'volume3': 'float'
            },
            'description': 'Gets and saves flow meter data'
        },
    ]
    return Response(routes)

from rest_framework import status


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def saveFlowData(request):
    try:
        if request.method == 'POST':
            data = request.data
        else:
            data = request.GET

        user_id = request.user.user_id  # Use the persistent UUID
        sensor_id = data.get('sensor_id', 'default')
        flow_data = []

        for i in range(1, 4):
            flow_rate = data.get(f'flowRate{i}')
            volume = data.get(f'volume{i}')
            
            if flow_rate is not None and volume is not None:
                flow_entry = {
                    'user': request.user.id,
                    'user_id': user_id,
                    'distributionID': i,
                    'sensor_id': sensor_id,
                    'flowRate': flow_rate,
                    'volume': volume
                }
                
                serializer = FlowDataSerializer(data=flow_entry)
                if serializer.is_valid():
                    serializer.save()
                    flow_data.append(serializer.data)
                else:
                    return Response({
                        'error': f'Validation failed for distribution {i}',
                        'details': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': 'Data saved successfully',
            'data': flow_data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserFlowData(request):
    try:
        # Get latest readings for each distribution point
        user_data = FlowData.objects.filter(user=request.user)
        latest_readings = {}
        
        for i in range(1, 4):
            reading = user_data.filter(distributionID=i).first()
            if reading:
                latest_readings[f'distribution{i}'] = FlowDataSerializer(reading).data
                
        return Response(latest_readings, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)