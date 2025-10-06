from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('send/<int:recipient_id>/', views.send_message, name='send_message'),
]