from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .forms import CustomUserCreationForm, ServiceProviderServiceForm, UserUpdateForm, DriverUpdateForm, ServiceProviderUpdateForm, CustomPasswordChangeForm
from .models import ServiceProvider, Driver
from bookings.models import AssistanceRequest # Import AssistanceRequest

class ServiceProviderServiceView(View):
    template_name = 'users/service_provider_services.html'

    @login_required
    def get(self, request):
        try:
            service_provider = request.user.serviceprovider
        except ServiceProvider.DoesNotExist:
            return redirect('some_error_page')

        form = ServiceProviderServiceForm(instance=service_provider)
        return render(request, self.template_name, {'form': form})

    @login_required
    def post(self, request):
        try:
            service_provider = request.user.serviceprovider
        except ServiceProvider.DoesNotExist:
            return redirect('some_error_page')

        form = ServiceProviderServiceForm(request.POST, instance=service_provider)
        if form.is_valid():
            form.save()
            return redirect('dashboard_provider')
        return render(request, self.template_name, {'form': form})

class ProfileSettingsView(View):
    template_name = 'users/profile_settings.html'

    @login_required
    def get(self, request):
        user_form = UserUpdateForm(instance=request.user)
        driver_form = None
        provider_form = None
        password_form = CustomPasswordChangeForm(user=request.user)

        if request.user.user_type == 'driver':
            try:
                driver_form = DriverUpdateForm(instance=request.user.driver)
            except Driver.DoesNotExist:
                pass # Handle case where driver profile might not exist
        elif request.user.user_type == 'provider':
            try:
                provider_form = ServiceProviderUpdateForm(instance=request.user.serviceprovider)
            except ServiceProvider.DoesNotExist:
                pass # Handle case where provider profile might not exist

        context = {
            'user_form': user_form,
            'driver_form': driver_form,
            'provider_form': provider_form,
            'password_form': password_form,
        }
        return render(request, self.template_name, context)

    @login_required
    def post(self, request):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        driver_form = None
        provider_form = None
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        forms_to_save = []
        if user_form.is_valid():
            forms_to_save.append(user_form)
        
        if request.user.user_type == 'driver':
            try:
                driver_form = DriverUpdateForm(request.POST, instance=request.user.driver)
                if driver_form.is_valid():
                    forms_to_save.append(driver_form)
            except Driver.DoesNotExist:
                pass
        elif request.user.user_type == 'provider':
            try:
                provider_form = ServiceProviderUpdateForm(request.POST, instance=request.user.serviceprovider)
                if provider_form.is_valid():
                    forms_to_save.append(provider_form)
            except ServiceProvider.DoesNotExist:
                pass

        if 'old_password' in request.POST: # Check if password form was submitted
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user) # Important to keep user logged in
                messages.success(request, 'Your password was successfully updated!')
                return redirect('users:profile_settings')
            else:
                messages.error(request, 'Please correct the error below.')
        
        all_valid = True
        for form in forms_to_save:
            if not form.is_valid():
                all_valid = False
                break

        if all_valid:
            for form in forms_to_save:
                form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile_settings') # Redirect back to settings page
        else:
            messages.error(request, 'Please correct the errors below.')

        context = {
            'user_form': user_form,
            'driver_form': driver_form,
            'provider_form': provider_form,
            'password_form': password_form,
        }
        return render(request, self.template_name, context)

@login_required
def user_request_history(request):
    requests = AssistanceRequest.objects.none() # Start with an empty queryset

    if hasattr(request.user, 'driver'):
        requests = AssistanceRequest.objects.filter(driver=request.user.driver).order_by('-created_at')
    elif hasattr(request.user, 'serviceprovider'):
        requests = AssistanceRequest.objects.filter(accepted_provider=request.user.serviceprovider).order_by('-created_at')
    elif request.user.is_superuser:
        requests = AssistanceRequest.objects.all().order_by('-created_at')
    
    context = {
        'requests': requests,
    }
    return render(request, 'request_history.html', context)

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            user_type = form.cleaned_data.get('user_type')
            if user_type == 'driver':
                Driver.objects.create(
                    user=user,
                    vehicle_type=form.cleaned_data.get('vehicle_type', ''),
                    license_plate=form.cleaned_data.get('license_plate', '')
                )
                messages.success(request, 'Driver account created successfully!')
            elif user_type == 'provider':
                provider = ServiceProvider.objects.create(
                    user=user,
                    company_name=form.cleaned_data.get('company_name', ''),
                    latitude=0.0,  # Default, should be updated
                    longitude=0.0, # Default, should be updated
                    address=form.cleaned_data.get('address', ''),
                    phone=form.cleaned_data.get('phone', '')
                )
                provider.services.set(form.cleaned_data.get('services'))
                messages.success(request, 'Service Provider account created successfully!')
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'users/profile.html')