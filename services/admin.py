from django.contrib import admin
from .models import ServiceCategory, Service, Pricing

admin.site.register(ServiceCategory)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration')
    search_fields = ('name',)

admin.site.register(Service, ServiceAdmin)

class PricingAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'base_fee', 'price_per_km', 'price_per_minute')
    search_fields = ('service_type',)

admin.site.register(Pricing, PricingAdmin)