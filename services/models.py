from django.db import models

class ServiceCategory(models.Model):
    name = models.CharField(max_length=50)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True) # e.g., estimated time for service

    def __str__(self):
        return self.name

class Pricing(models.Model):
    service_type = models.CharField(max_length=20, choices=[
        ('towing', 'Towing'),
        ('mechanic', 'Mechanic'),
        ('vulcanizing', 'Vulcanizing'),
    ])
    base_fee = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_km = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_minute = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.service_type} - Base: {self.base_fee}, Per Km: {self.price_per_km}"
