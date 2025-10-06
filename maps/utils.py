import math
import random
from users.models import ServiceProvider

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c  # Distance in kilometers

def get_nearby_providers(user_lat, user_lon, service_types=None, max_distance_km=10):
    """Get nearby service providers within specified distance"""
    providers = ServiceProvider.objects.filter(is_available=True, is_verified=True)
    
    if service_types:
        # Filter providers that offer any of the requested service types
        providers = providers.filter(services__name__in=service_types).distinct()
    
    nearby_providers = []
    for provider in providers:
        distance = calculate_distance(user_lat, user_lon, provider.latitude, provider.longitude)
        if distance <= max_distance_km:
            provider.distance = round(distance, 2)
            provider.eta = calculate_eta(distance)
            nearby_providers.append(provider)
    
    # Sort by distance
    nearby_providers.sort(key=lambda x: x.distance)
    return nearby_providers

def calculate_eta(distance_km):
    """Calculate estimated time of arrival in minutes"""
    # Assuming average speed of 30 km/h in urban areas
    average_speed_kmh = 30
    travel_time_hours = distance_km / average_speed_kmh
    eta_minutes = int(travel_time_hours * 60)
    
    # Add buffer for traffic and preparation
    eta_minutes += 5
    
    return max(5, eta_minutes)  # Minimum 5 minutes

def generate_sample_providers(user_lat, user_lon, count=10):
    """Generate sample providers around user location for demo"""
    providers = []
    service_types = ['towing', 'mechanic', 'vulcanizing', 'parts', 'washing']
    
    for i in range(count):
        # Generate random location within 5km radius
        offset_lat = random.uniform(-0.045, 0.045)  # ~5km
        offset_lon = random.uniform(-0.045, 0.045)  # ~5km
        
        provider_lat = user_lat + offset_lat
        provider_lon = user_lon + offset_lon
        
        providers.append({
            'id': i + 1,
            'company_name': f'Service Provider {i+1}',
            'service_type': random.choice(service_types),
            'latitude': provider_lat,
            'longitude': provider_lon,
            'rating': round(random.uniform(3.5, 5.0), 1),
            'distance': calculate_distance(user_lat, user_lon, provider_lat, provider_lon),
            'eta': calculate_eta(calculate_distance(user_lat, user_lon, provider_lat, provider_lon)),
            'is_available': True
        })
    
    return sorted(providers, key=lambda x: x['distance'])
