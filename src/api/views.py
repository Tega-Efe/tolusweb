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
                'user': 'integer',  # ForeignKey to CustomUser
                'sensor_id': 'string',  # CharField with default='default'
                'distributionID': 'integer',  # Required IntegerField
                'flowRate': 'float',  # Optional FloatField
                'volume': 'float',  # Optional FloatField
            },
            'description': 'Gets and saves flow meter data for a single distribution point'
        },
        {
            'Endpoint': '/user-flow-data/',
            'method': 'GET',
            'description': 'Gets all flow data for the authenticated user'
        }
    ]
    return Response(routes)

from rest_framework import status

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def saveSensorData(request):
    try:
        data = request.data if request.method == 'POST' else request.GET
        sensor_id = data.get('sensor_id')
        flow_rate = data.get('flowRate')
        volume = data.get('volume')

        if not all([sensor_id, flow_rate, volume]):
            return Response({
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Convert sensor_id to distributionID (1-3)
        distribution_id = int(sensor_id)

        distribution_data = {
            'distributionID': distribution_id,
            'sensor_id': f'sensor_{sensor_id}',
            'flowRate': float(flow_rate),
            'volume': float(volume)
        }

        serializer = FlowDataSerializer(data=distribution_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateUserFlowData(request):
    try:
        user = request.user
        data = request.data
        flow_data = []

        for i in range(1, 4):
            distribution_data = {
                'user': user.id,
                'user_id': user.user_id,
                'distributionID': i,
                'sensor_id': f'sensor_{i}',
                'flowRate': data.get(f'flowRate{i}'),
                'volume': data.get(f'volume{i}')
            }
            
            if all(v is not None for v in [distribution_data['flowRate'], distribution_data['volume']]):
                # Try to update existing record first
                instance = FlowData.objects.filter(
                    user=user,
                    distributionID=i
                ).first()
                
                if instance:
                    serializer = FlowDataSerializer(instance, data=distribution_data)
                else:
                    serializer = FlowDataSerializer(data=distribution_data)

                if serializer.is_valid():
                    serializer.save()
                    flow_data.append(serializer.data)
                else:
                    return Response({
                        'error': f'Validation failed for distribution {i}',
                        'details': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)

        formatted_response = {
            f'distribution{entry["distributionID"]}': entry 
            for entry in flow_data
        }

        return Response(formatted_response, status=status.HTTP_201_CREATED)

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