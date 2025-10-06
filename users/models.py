from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('driver', 'Driver'),
        ('provider', 'Service Provider'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='driver')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=50)
    license_plate = models.CharField(max_length=20)
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"Driver: {self.user.username}"

class ServiceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    services = models.ManyToManyField('services.ServiceCategory')
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField()
    phone = models.CharField(max_length=15)
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"{self.company_name} ({', '.join(self.services.values_list('name', flat=True))})"
