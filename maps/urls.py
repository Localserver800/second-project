from django.urls import path
from . import views

app_name = 'maps'

urlpatterns = [
    path('live-map/', views.live_map, name='live_map'),
    path('request-assistance/', views.request_assistance_map, name='request_assistance_map'),
    path('active-tracking/<uuid:tracking_id>/', views.active_tracking, name='active_tracking'),
    path('api/nearby-providers/', views.get_nearby_providers_api, name='nearby_providers_api'),
    path('api/tracking-updates/<uuid:tracking_id>/', views.get_tracking_updates, name='tracking_updates'),
    path('api/update-provider-location/', views.update_provider_location, name='update_provider_location'),
    path('api/simulate-movement/<uuid:tracking_id>/', views.simulate_provider_movement, name='simulate_movement'),
]