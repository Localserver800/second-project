from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
import datetime
from .models import AssistanceRequest
from users.models import ServiceProvider, Driver
from services.models import ServiceCategory

@csrf_exempt
@login_required
def create_assistance_request_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            provider_id = data.get('provider_id')
            service_category_name = data.get('service_type')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            description = data.get('description')

            # Ensure user is a driver
            if not hasattr(request.user, 'driver'):
                return JsonResponse({'success': False, 'error': 'Only drivers can create assistance requests.'}, status=403)

            driver = request.user.driver
            service_provider = get_object_or_404(ServiceProvider, id=provider_id)
            service_category = get_object_or_404(ServiceCategory, name=service_category_name)

            # Create AssistanceRequest
            assistance_request = AssistanceRequest.objects.create(
                driver=driver,
                accepted_provider=service_provider,
                service_type=service_category.name, # Store the name of the service category
                latitude=latitude,
                longitude=longitude,
                description=description,
                status='pending', # Initial status
                tracking_id=uuid.uuid4() # Generate a unique tracking ID
            )

            return JsonResponse({'success': True, 'tracking_id': str(assistance_request.tracking_id)})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
        except (ServiceProvider.DoesNotExist, ServiceCategory.DoesNotExist) as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@login_required
def accept_request(request, request_id):
    assistance_request = get_object_or_404(AssistanceRequest, id=request_id)
    
    if not hasattr(request.user, 'serviceprovider'):
        messages.error(request, 'Only service providers can accept requests.')
        return redirect('dashboard')
        
    if assistance_request.status != 'pending':
        messages.warning(request, 'This request is no longer pending.')
        return redirect('dashboard')
        
    assistance_request.accepted_provider = request.user.serviceprovider
    assistance_request.status = 'accepted'
    assistance_request.save()
    
    messages.success(request, f'You have accepted request #{assistance_request.id}.')
    return redirect('dashboard')

@login_required
def start_service(request, request_id):
    assistance_request = get_object_or_404(AssistanceRequest, id=request_id)
    
    if assistance_request.accepted_provider != request.user.serviceprovider:
        messages.error(request, 'You are not assigned to this request.')
        return redirect('dashboard')
        
    assistance_request.status = 'in_progress'
    assistance_request.save()
    
    messages.info(request, f'Service for request #{assistance_request.id} has started.')
    return redirect('dashboard')

@login_required
def complete_service(request, request_id):
    assistance_request = get_object_or_404(AssistanceRequest, id=request_id)
    
    if assistance_request.accepted_provider != request.user.serviceprovider:
        messages.error(request, 'You are not assigned to this request.')
        return redirect('dashboard')
        
    assistance_request.status = 'completed'
    assistance_request.completed_at = datetime.datetime.now()
    assistance_request.save()
    
    messages.success(request, f'Service for request #{assistance_request.id} has been completed.')
    return redirect('dashboard')

@login_required
def cancel_request(request, request_id):
    assistance_request = get_object_or_404(AssistanceRequest, id=request_id)
    
    if not hasattr(request.user, 'driver') or assistance_request.driver != request.user.driver:
        messages.error(request, 'You are not authorized to cancel this request.')
        return redirect('dashboard')
        
    if assistance_request.status not in ['pending', 'accepted', 'in_progress']:
        messages.warning(request, 'This request cannot be cancelled.')
        return redirect('dashboard')
        
    assistance_request.status = 'cancelled'
    assistance_request.save()
    
    messages.success(request, f'Request #{assistance_request.id} has been cancelled.')
    return redirect('dashboard')