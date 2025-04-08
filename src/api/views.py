from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import FlowDataSerializer, TokenHistorySerializer
from decimal import Decimal
from .models import FlowData, TokenHistory
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .utils import *

@api_view(['GET'])
def getRoutes(request):
    routes = [
        {
            'Endpoint': '/api/flow-data/',
            'method': 'GET, POST',
            'body': {
                'user': 'integer',
                'sensor_id': 'string',
                'distributionID': 'integer',
                'flowRate': 'float',
                'volume': 'float',
            },
            'description': 'Create or get single flow meter reading'
        },
        {
            'Endpoint': '/api/flow-data/user/',
            'method': 'GET',
            'description': 'Get all flow data for authenticated user'
        },
        {
            'Endpoint': '/api/token/recharge/',
            'method': 'POST',
            'body': {'sensor_id': 'string', 'token_amount': 'decimal'},
            'description': 'Recharge water token for a sensor'
        },
        {
            'Endpoint': '/api/token/history/',
            'method': 'GET',
            'description': 'Get token and usage history for authenticated user'
        }
    ]
    return Response(routes)

from rest_framework import status
from django.utils import timezone

@api_view(['GET', 'POST'])
def saveSensorData(request):
    try:
        data = request.data if request.method == 'POST' else request.GET
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        last_users = User.objects.order_by('-created')[:3]
        
        print("\n----- Incoming Sensor Data -----")
        print(f"Request Method: {request.method}")
        print(f"Raw Data: {data}")
        
        try:
            sensor_id = int(data.get('sensor_id', 0))
            flow_rate = float(data.get('flowRate', 0))
            volume = float(data.get('volume', 0))
            
            if sensor_id <= 0:
                raise ValueError("sensor_id must be positive")
                
        except (TypeError, ValueError) as e:
            print(f"\nError: Invalid data format - {str(e)}")
            return Response({
                'error': 'Invalid data format',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print("\n----- Extracted Values -----")
        print(f"Sensor ID: {sensor_id}")
        print(f"Flow Rate: {flow_rate}")
        print(f"Volume: {volume}")

        try:
            user_index = sensor_id - 1
            if user_index < 0 or user_index >= len(last_users):
                raise IndexError(f"No user found for sensor {sensor_id}")
            assigned_user = last_users[user_index]
            print(f"\nAssigned User: {assigned_user.username}")
        except (ValueError, IndexError) as e:
            print(f"\nError: Invalid sensor_id {sensor_id} - {str(e)}")
            return Response({
                'error': 'Invalid sensor ID',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # Save flow data first
        sensor_data = {
            'user': assigned_user.id,
            'sensor_id': str(sensor_id),
            'flowRate': flow_rate,
            'volume': volume
        }

        instance = FlowData.objects.filter(
            user=assigned_user,
            sensor_id=str(sensor_id)
        ).first()

        # Get active token with remaining volume
        active_token = TokenHistory.objects.filter(
            user=assigned_user,
            sensor_id=str(sensor_id),
            is_active=True,
            remaining_volume__gt=0
        ).first()

        # If no active token, reset flow data to 0 and return early
        if not active_token:
            # Reset flow data to 0 if it exists
            if instance:
                reset_data = {
                    'user': assigned_user.id,
                    'sensor_id': str(sensor_id),
                    'flowRate': 0,
                    'volume': 0
                }
                serializer = FlowDataSerializer(instance, data=reset_data)
                if serializer.is_valid():
                    serializer.save()

            return Response({
                'error': 'No active token or insufficient balance',
                'remaining_volume': 0,
                'flowRate': 0,
                'volume': 0
            }, status=status.HTTP_400_BAD_REQUEST)


        # Calculate and update volume used if there's an active token
        if active_token:
            previous_reading = FlowData.objects.filter(
                user=assigned_user,
                sensor_id=str(sensor_id)
            ).order_by('-created').first()

            # Only process if current volume is greater than previous reading
            current_volume = volume
            last_recorded_volume = previous_reading.volume if previous_reading else 0
            
            if current_volume > last_recorded_volume:
                volume_used = current_volume - last_recorded_volume
                
                if volume_used > 0:
                    active_token.volume_used += Decimal(str(volume_used))
                    active_token.remaining_volume -= Decimal(str(volume_used))
                    
                    if active_token.remaining_volume <= 0:
                        # Create final history entry for depleted token
                        TokenHistory.objects.create(
                            user=assigned_user,
                            sensor_id=str(sensor_id),
                            token_amount=active_token.token_amount,
                            volume_limit=active_token.volume_limit,
                            volume_used=active_token.volume_limit,
                            remaining_volume=Decimal('0.0'),
                            is_active=False,
                            start_date=active_token.start_date,
                            last_updated=active_token.last_updated,
                            end_date=timezone.now()
                        )

                        # Reset flow data to 0
                        reset_data = {
                            'user': assigned_user.id,
                            'sensor_id': str(sensor_id),
                            'flowRate': 0,
                            'volume': 0
                        }
                        if instance:
                            serializer = FlowDataSerializer(instance, data=reset_data)
                            if serializer.is_valid():
                                serializer.save()
                        
                        print(f"\nToken depleted for sensor {sensor_id}")
                        return Response({
                            'message': 'Token depleted',
                            'remaining_volume': 0
                        }, status=status.HTTP_200_OK)
                    else:
                        active_token.last_updated = timezone.now()
                        active_token.save()

            # Save flow data only if active token exists and has remaining volume
            if active_token.remaining_volume > 0:
                if instance:
                    serializer = FlowDataSerializer(instance, data=sensor_data)
                else:
                    serializer = FlowDataSerializer(data=sensor_data)

                if serializer.is_valid():
                    serializer.save()
                    response_data = serializer.data
                    
                    token_info = {
                        'token_amount': float(active_token.token_amount),
                        'remaining_volume': float(active_token.remaining_volume),
                        'is_active': True
                    }
                    response_data.update(token_info)
                    
                    print("\nData saved successfully!")
                    return Response(response_data, status=status.HTTP_201_CREATED)
                
                print(f"\nValidation Error: {serializer.errors}")
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'No active token or insufficient balance',
                'remaining_volume': 0
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(f"\nException occurred: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rechargeToken(request):
    try:
        User = get_user_model()
        last_users = list(User.objects.order_by('-created')[:3])
        user_index = last_users.index(request.user)
        sensor_id = str(user_index + 1)

        token_amount = Decimal(request.data.get('token_amount', '0'))
        if token_amount <= 0:
            return Response({
                'error': 'Invalid token amount'
            }, status=status.HTTP_400_BAD_REQUEST)

        volume_to_add = token_amount * 10
        current_time = timezone.now()

        active_token = TokenHistory.objects.filter(
            user=request.user,
            sensor_id=sensor_id,
            is_active=True
        ).first()

        if active_token and active_token.remaining_volume > 0:
            # Save history of previous state before update
            TokenHistory.objects.create(
                user=request.user,
                sensor_id=sensor_id,
                token_amount=active_token.token_amount,
                volume_limit=active_token.volume_limit,
                volume_used=active_token.volume_used,
                remaining_volume=active_token.remaining_volume,
                is_active=False,
                start_date=active_token.start_date,
                last_updated=active_token.last_updated,
                end_date=current_time
            )

            
            
            serializer = TokenHistorySerializer(active_token)
        else:
            # Create new active token only if none exists
            token_data = {
                'user': request.user.id,
                'sensor_id': sensor_id,
                'token_amount': token_amount,
                'volume_limit': volume_to_add,
                'remaining_volume': volume_to_add,
                'volume_used': Decimal('0.0'),
                'is_active': True,
                'start_date': current_time,
                'last_updated': current_time
            }
            serializer = TokenHistorySerializer(data=token_data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"\nError in rechargeToken: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserFlowData(request):
    try:
        # Get user's sensor ID by finding their position in last 3 users
        User = get_user_model()
        last_users = list(User.objects.order_by('-created')[:3])  # Convert QuerySet to list
        try:
            user_index = last_users.index(request.user)
            sensor_id = str(user_index + 1)
        except ValueError:
            return Response({
                'error': 'User not in last 3 registered users'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get flow and token data for user's sensor
        user_data = FlowData.objects.filter(
            user=request.user,
            sensor_id=sensor_id
        ).first()
        
        active_token = TokenHistory.objects.filter(
            user=request.user,
            sensor_id=sensor_id,
            is_active=True,
            remaining_volume__gt=0
        ).first()
        
        response_data = {}
        
        if user_data:
            reading_data = FlowDataSerializer(user_data).data
            # Set token info with dates
            token_info = {
                'token_amount': float(active_token.token_amount) if active_token else 0.0,
                'remaining_volume': float(active_token.remaining_volume) if active_token else 0.0,
                'is_active': bool(active_token and active_token.remaining_volume > 0),
                'start_date': active_token.start_date if active_token else None,
                'last_updated': active_token.last_updated if active_token else None,
                'end_date': active_token.end_date if active_token else None
            }
            reading_data.update(token_info)
            response_data[f'sensor{sensor_id}'] = reading_data
                
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"\nError in getUserFlowData: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getTokenHistory(request):
    try:
        # Get user's sensor ID
        User = get_user_model()
        last_users = list(User.objects.order_by('-created')[:3])  # Convert QuerySet to list
        try:
            user_index = last_users.index(request.user)
            sensor_id = str(user_index + 1)
        except ValueError:
            return Response({
                'error': 'User not in last 3 registered users'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get ALL token history for user's sensor, not just active ones
        history = TokenHistory.objects.filter(
            user=request.user,
            sensor_id=sensor_id
        ).order_by('-start_date')
        
        if not history.exists():
            return Response([], status=status.HTTP_200_OK)
            
        serializer = TokenHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"\nError in getTokenHistory: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)