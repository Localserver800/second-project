from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('manage-services/', views.ServiceProviderServiceView.as_view(), name='manage_services'),
    path('settings/', views.ProfileSettingsView.as_view(), name='profile_settings'),
]