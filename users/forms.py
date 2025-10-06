from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import User, ServiceProvider, Driver
from services.models import ServiceCategory

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class ServiceProviderSignUpForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    address = forms.CharField(max_length=255, required=True)

    class Meta:
        model = ServiceProvider
        fields = ('company_name', 'latitude', 'longitude', 'address', 'phone', 'is_verified', 'is_available', 'rating', 'services')

class ServiceProviderServiceForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=ServiceCategory.objects.all(),
        widget=forms.SelectMultiple,
        required=False
    )

    class Meta:
        model = ServiceProvider
        fields = ('services',)

# New forms for profile settings
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'address')

class DriverUpdateForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ('vehicle_type', 'license_plate', 'current_latitude', 'current_longitude')

class ServiceProviderUpdateForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = ('company_name', 'latitude', 'longitude', 'address', 'phone', 'is_available')

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'