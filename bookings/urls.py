from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('api/create-request/', views.create_assistance_request_api, name='create_assistance_request_api'),
    path('accept/<int:request_id>/', views.accept_request, name='accept_request'),
    path('start/<int:request_id>/', views.start_service, name='start_service'),
    path('complete/<int:request_id>/', views.complete_service, name='complete_service'),
    path('cancel/<int:request_id>/', views.cancel_request, name='cancel_request'),
]