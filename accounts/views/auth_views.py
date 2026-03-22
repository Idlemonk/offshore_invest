from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def homepage(request):
    """Homepage view"""
    return render(request, 'accounts/homepage.html')

def signup(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('accounts:homepage')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Offshore Investment, {user.username}!")
            return redirect('accounts:homepage')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('accounts:homepage')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('accounts:homepage')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('accounts:homepage')
