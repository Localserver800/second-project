
from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .forms import CustomUserCreationForm, ServiceProviderServiceForm, UserUpdateForm, DriverUpdateForm, ServiceProviderUpdateForm, CustomPasswordChangeForm
from .models import ServiceProvider, Driver
from bookings.models import AssistanceRequest

class ServiceProviderServiceView(LoginRequiredMixin, View):
    template_name = 'users/service_provider_services.html'

    def get(self, request):
        try:
            service_provider = request.user.serviceprovider
        except ServiceProvider.DoesNotExist:
            return redirect('some_error_page')

        form = ServiceProviderServiceForm(instance=service_provider)
        return render(request, self.template_name, {'form': form})

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

class AccountSettingsView(LoginRequiredMixin, View):
    template_name = 'users/settings_account.html'

    def get(self, request):
        user_form = UserUpdateForm(instance=request.user)
        context = {'user_form': user_form}
        return render(request, self.template_name, context)

    def post(self, request):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your account has been updated.')
            return redirect('users:settings')
        context = {'user_form': user_form}
        return render(request, self.template_name, context)

class SecuritySettingsView(LoginRequiredMixin, View):
    template_name = 'users/settings_security.html'

    def get(self, request):
        password_form = CustomPasswordChangeForm(user=request.user)
        context = {'password_form': password_form}
        return render(request, self.template_name, context)

    def post(self, request):
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('users:settings_security')
        context = {'password_form': password_form}
        return render(request, self.template_name, context)

class PaymentSettingsView(LoginRequiredMixin, View):
    template_name = 'users/settings_payment.html'

    def get(self, request):
        return render(request, self.template_name)

@login_required
def user_request_history(request):
    requests = AssistanceRequest.objects.none()

    if hasattr(request.user, 'driver'):
        requests = AssistanceRequest.objects.filter(driver=request.user.driver).order_by('-created_at')
    elif hasattr(request.user, 'serviceprovider'):
        requests = AssistanceRequest.objects.filter(accepted_provider=request.user.serviceprovider).order_by('-created_at')
    elif request.user.is_superuser:
        requests = AssistanceRequest.objects.all().order_by('-created_at')
    
    context = {'requests': requests}
    return render(request, 'request_history.html', context)

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'users/profile.html')
