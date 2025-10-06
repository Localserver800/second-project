from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import User, ServiceProvider, Driver
from services.models import ServiceCategory
from django.db import transaction


class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, required=True)
    company_name = forms.CharField(max_length=100, required=False)
    address = forms.CharField(max_length=255, required=False)
    phone = forms.CharField(max_length=15, required=False)
    services = forms.ModelMultipleChoiceField(
        queryset=ServiceCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    vehicle_type = forms.CharField(max_length=50, required=False)
    license_plate = forms.CharField(max_length=20, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type')

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")

        if user_type == 'provider':
            if not cleaned_data.get('company_name'):
                self.add_error('company_name', 'This field is required for service providers.')
            if not cleaned_data.get('address'):
                self.add_error('address', 'This field is required for service providers.')
            if not cleaned_data.get('phone'):
                self.add_error('phone', 'This field is required for service providers.')
            if not cleaned_data.get('services'):
                self.add_error('services', 'Please select at least one service.')

        elif user_type == 'driver':
            if not cleaned_data.get('vehicle_type'):
                self.add_error('vehicle_type', 'This field is required for drivers.')
            if not cleaned_data.get('license_plate'):
                self.add_error('license_plate', 'This field is required for drivers.')

        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()

        user_type = self.cleaned_data.get('user_type')
        if user_type == 'driver':
            Driver.objects.create(
                user=user,
                vehicle_type=self.cleaned_data.get('vehicle_type', ''),
                license_plate=self.cleaned_data.get('license_plate', '')
            )
        elif user_type == 'provider':
            provider = ServiceProvider.objects.create(
                user=user,
                company_name=self.cleaned_data.get('company_name', ''),
                latitude=0.0,
                longitude=0.0,
                address=self.cleaned_data.get('address', ''),
                phone=self.cleaned_data.get('phone', '')
            )
            provider.services.set(self.cleaned_data.get('services'))

        return user


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
        fields = (
        'company_name', 'latitude', 'longitude', 'address', 'phone', 'is_verified', 'is_available', 'rating',
        'services')


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
