from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bookings.models import AssistanceRequest
from users.models import Driver, ServiceProvider
from django.db.models import Count, Q

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    context = {}
    if hasattr(request.user, 'driver'):
        template = 'dashboard_driver.html'
        requests = AssistanceRequest.objects.filter(driver=request.user.driver)
        context = {
            'total_requests': requests.count(),
            'completed_requests': requests.filter(status='completed').count(),
            'active_requests_count': requests.filter(status__in=['pending', 'accepted', 'in_progress']).count(),
            'active_request': requests.filter(status__in=['pending', 'accepted', 'in_progress']).first(),
            'recent_requests': requests.order_by('-created_at')[:3],
        }
    elif hasattr(request.user, 'serviceprovider'):
        template = 'dashboard_provider.html'
        provider = request.user.serviceprovider
        jobs = AssistanceRequest.objects.filter(accepted_provider=provider)
        context = {
            'total_jobs': jobs.count(),
            'completed_jobs': jobs.filter(status='completed').count(),
            'pending_jobs_count': AssistanceRequest.objects.filter(status='pending', service_type=provider.service_type).count(),
            'rating': provider.rating,
            'new_requests': AssistanceRequest.objects.filter(status='pending', service_type=provider.service_type)[:2],
            'active_jobs': jobs.filter(status__in=['accepted', 'in_progress']),
        }
    elif request.user.is_superuser:
        template = 'dashboard_admin.html'
        context = {
            'total_requests': AssistanceRequest.objects.count(),
            'service_stats': AssistanceRequest.objects.values('service_type').annotate(count=Count('id')),
            'status_stats': AssistanceRequest.objects.values('status').annotate(count=Count('id')),
            'total_drivers': Driver.objects.count(),
            'total_providers': ServiceProvider.objects.count(),
            'active_requests': AssistanceRequest.objects.filter(status__in=['pending', 'accepted', 'in_progress']).order_by('-created_at'),
        }
    else:
        template = 'home.html'
    
    return render(request, template, context)



@login_required
def request_history(request):
    if not hasattr(request.user, 'driver'):
        messages.error(request, 'Only drivers can view request history.')
        return redirect('dashboard')
    
    requests = AssistanceRequest.objects.filter(driver=request.user.driver).order_by('-created_at')
    context = {
        'requests': requests,
    }
    return render(request, 'request_history.html', context)

@login_required
def admin_active_requests(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    requests = AssistanceRequest.objects.filter(status__in=['pending', 'accepted', 'in_progress']).order_by('-created_at')
    context = {
        'requests': requests,
    }
    return render(request, 'admin_active_requests.html', context)

@login_required
def admin_request_history(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    requests = AssistanceRequest.objects.all().order_by('-created_at')
    context = {
        'requests': requests,
    }
    return render(request, 'admin_request_history.html', context)