from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'your@email.com'
    }))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Last Name'
    }))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': '+91 9876543210'
    }))
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Your City'
    }))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['username', 'password1', 'password2']:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get('phone', '')
            profile.city = self.cleaned_data.get('city', '')
            profile.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Username', 'id': 'id_login_username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Password', 'id': 'id_login_password'
    }))


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name  = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email      = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['phone', 'city', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'city':  forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
