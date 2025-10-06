from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from main import views as main_views
from users import views as user_views
from maps import views as maps_views

urlpatterns = [
    path('admin/request-history/', main_views.admin_request_history, name='admin_request_history'),
    path('admin/', admin.site.urls),
    path('', main_views.home, name='home'),
    path('dashboard/', main_views.dashboard, name='dashboard'),
    path('request-assistance/', maps_views.live_map, name='request_assistance'),
    path('maps/', include('maps.urls')),
    path('request-history/', user_views.user_request_history, name='request_history'),
    path('admin/request-history/', main_views.admin_request_history, name='admin_request_history'),
    path('maps/', include('maps.urls')),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('messages/', include('communication.urls')),
    path('bookings/', include('bookings.urls')),
    path('users/', include('users.urls')),
]
