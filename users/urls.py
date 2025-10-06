
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('manage-services/', views.ServiceProviderServiceView.as_view(), name='manage_services'),
    
    # New Settings URLs
    path('settings/', views.AccountSettingsView.as_view(), name='settings'),
    path('settings/security/', views.SecuritySettingsView.as_view(), name='settings_security'),
    path('settings/payment/', views.PaymentSettingsView.as_view(), name='settings_payment'),
]
