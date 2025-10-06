from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from .utils import get_nearby_providers, generate_sample_providers
from bookings.models import AssistanceRequest, ProviderLocation, TripTracking
from users.models import ServiceProvider
from .utils import calculate_distance, calculate_eta
import datetime
from django.views.decorators.csrf import csrf_exempt

@login_required
def live_map(request):
    """Main map view showing user location and nearby providers"""
    from services.models import ServiceCategory
    # Default coordinates (Accra, Ghana)
    default_lat = 5.6037
    default_lon = -0.1870
    
    context = {
        'default_lat': default_lat,
        'default_lon': default_lon,
        'service_categories': ServiceCategory.objects.all(),
    }
    return render(request, 'maps/live_map.html', context)

@login_required
def get_nearby_providers_api(request):
    """API endpoint to get nearby providers"""
    try:
        user_lat = float(request.GET.get('lat', 5.6037))
        user_lon = float(request.GET.get('lon', -0.1870))
        service_types = request.GET.getlist('service_type') # Get a list of service types
        
        # Get providers from database
        providers = get_nearby_providers(user_lat, user_lon, service_types)
        
        # Format data for API response
        providers_data = [
            {
                'id': p.id,
                'company_name': p.company_name,
                'latitude': p.latitude,
                'longitude': p.longitude,
                'services': [s.name for s in p.services.all()], # Get all service names
                'rating': p.rating,
                'distance': calculate_distance(user_lat, user_lon, p.latitude, p.longitude),
                'eta': calculate_eta(calculate_distance(user_lat, user_lon, p.latitude, p.longitude))
            }
            for p in providers
        ]
        
        return JsonResponse({
            'success': True,
            'providers': providers_data,
            'user_location': {'lat': user_lat, 'lon': user_lon}
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def request_assistance_map(request):
    """Request assistance with map interface"""
    if request.method == 'POST':
        service_type = request.POST.get('service_type')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        description = request.POST.get('description')
        
        # Process the assistance request
        # This would create a new AssistanceRequest in a real scenario
        
        return JsonResponse({
            'success': True,
            'message': 'Assistance request submitted successfully!',
            'request_id': 123  # Demo ID
        })
    
    from services.models import ServiceCategory
    context = {
        'default_lat': 5.6037,
        'default_lon': -0.1870,
        'service_categories': ServiceCategory.objects.all(),
    }
    return render(request, 'maps/request_assistance.html', context)

@login_required
def active_tracking(request, tracking_id):
    """Live tracking page for an active assistance request"""
    try:
        assistance_request = AssistanceRequest.objects.get(tracking_id=tracking_id)
        
        # Check if user has permission to view this tracking
        if (request.user != assistance_request.driver.user and 
            (not hasattr(request.user, 'serviceprovider') or 
             request.user.serviceprovider != assistance_request.accepted_provider)):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        context = {
            'assistance_request': assistance_request,
            'tracking_id': tracking_id,
        }
        return render(request, 'maps/active_tracking.html', context)
        
    except AssistanceRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found'}, status=404)

@csrf_exempt
def update_provider_location(request):
    """API for provider app to update their location (simulated for demo)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tracking_id = data.get('tracking_id')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            assistance_request = AssistanceRequest.objects.get(tracking_id=tracking_id)
            
            # Create location update
            ProviderLocation.objects.create(
                provider=assistance_request.accepted_provider,
                assistance_request=assistance_request,
                latitude=latitude,
                longitude=longitude
            )
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required
def get_tracking_updates(request, tracking_id):
    """API to get latest tracking updates for a request"""
    try:
        assistance_request = AssistanceRequest.objects.get(tracking_id=tracking_id)
        
        # Get latest provider location
        latest_location = ProviderLocation.objects.filter(
            assistance_request=assistance_request
        ).order_by('-timestamp').first()
        
        # Calculate ETA and distance
        if latest_location:
            distance = calculate_distance(
                latest_location.latitude, latest_location.longitude,
                assistance_request.latitude, assistance_request.longitude
            )
            eta = calculate_eta(distance)
            
            # Get recent location history for route line
            recent_locations = ProviderLocation.objects.filter(
                assistance_request=assistance_request
            ).order_by('-timestamp')[:10]
            
            location_history = [
                {'lat': loc.latitude, 'lon': loc.longitude}
                for loc in recent_locations
            ]
            
            return JsonResponse({
                'success': True,
                'provider_location': {
                    'lat': latest_location.latitude,
                    'lon': latest_location.longitude,
                    'timestamp': latest_location.timestamp.isoformat()
                },
                'user_location': {
                    'lat': assistance_request.latitude,
                    'lon': assistance_request.longitude
                },
                'distance': round(distance, 2),
                'eta': eta,
                'location_history': location_history,
                'status': assistance_request.status
            })
        else:
            return JsonResponse({
                'success': True,
                'provider_location': None,
                'user_location': {
                    'lat': assistance_request.latitude,
                    'lon': assistance_request.longitude
                },
                'status': assistance_request.status
            })
            
    except AssistanceRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found'}, status=404)

@login_required
def simulate_provider_movement(request, tracking_id):
    """Simulate provider moving towards user (for demo purposes)"""
    try:
        assistance_request = AssistanceRequest.objects.get(tracking_id=tracking_id)
        
        if assistance_request.status != 'accepted':
            return JsonResponse({'error': 'Request not accepted yet'})
        
        # Get provider's current location or start from their base
        latest_location = ProviderLocation.objects.filter(
            assistance_request=assistance_request
        ).order_by('-timestamp').first()
        
        if latest_location:
            current_lat = latest_location.latitude
            current_lon = latest_location.longitude
        else:
            # Start from provider's registered location
            current_lat = assistance_request.accepted_provider.latitude
            current_lon = assistance_request.accepted_provider.longitude
        
        # Calculate direction towards user
        user_lat = assistance_request.latitude
        user_lon = assistance_request.longitude
        
        # Move 10% closer to user
        new_lat = current_lat + (user_lat - current_lat) * 0.1
        new_lon = current_lon + (user_lon - current_lon) * 0.1
        
        # Create new location update
        ProviderLocation.objects.create(
            provider=assistance_request.accepted_provider,
            assistance_request=assistance_request,
            latitude=new_lat,
            longitude=new_lon
        )
        
        # Calculate remaining distance
        remaining_distance = calculate_distance(new_lat, new_lon, user_lat, user_lon)
        
        # If very close, mark as arrived
        if remaining_distance < 0.1:  # 100 meters
            assistance_request.status = 'in_progress'
            assistance_request.save()
        
        return JsonResponse({
            'success': True,
            'new_location': {'lat': new_lat, 'lon': new_lon},
            'remaining_distance': round(remaining_distance, 2),
            'status': assistance_request.status
        })
        
    except AssistanceRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found'}, status=404)
