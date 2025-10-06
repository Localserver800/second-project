from django.db import models
import uuid
from users.models import Driver, ServiceProvider

class AssistanceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_provider = models.ForeignKey(ServiceProvider, null=True, blank=True, on_delete=models.SET_NULL)
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    tracking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    def __str__(self):
        return f"Request #{self.id} - {self.driver.user.username}"

class Review(models.Model):
    booking = models.OneToOneField(AssistanceRequest, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for Booking #{self.booking.id}"

class ProviderLocation(models.Model):
    """Store real-time provider locations for tracking"""
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    assistance_request = models.ForeignKey(AssistanceRequest, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now=True)
    speed = models.FloatField(null=True, blank=True)  # km/h
    heading = models.FloatField(null=True, blank=True)  # degrees
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.provider.company_name} - {self.timestamp}"

class TripTracking(models.Model):
    """Track the entire trip progress"""
    assistance_request = models.OneToOneField(AssistanceRequest, on_delete=models.CASCADE)
    provider_start_lat = models.FloatField()
    provider_start_lon = models.FloatField()
    destination_lat = models.FloatField()
    destination_lon = models.FloatField()
    started_at = models.DateTimeField(auto_now_add=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    route_polyline = models.TextField(blank=True)  # Store route coordinates
    
    def __str__(self):
        return f"Trip #{self.assistance_request.id}"