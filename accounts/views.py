from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from .models import UserProfile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('scanner:dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Account created successfully.')
            return redirect('scanner:dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('scanner:dashboard')

    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect(request.GET.get('next', 'scanner:dashboard'))
            else:
                messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out. Stay safe online! 🛡️')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name  = form.cleaned_data['last_name']
            request.user.email      = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(
            instance=profile,
            initial={
                'first_name': request.user.first_name,
                'last_name':  request.user.last_name,
                'email':      request.user.email,
            }
        )

    from scanner.models import ScanHistory
    recent_scans = ScanHistory.objects.filter(user=request.user)[:5]
    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile,
        'recent_scans': recent_scans,
    })
