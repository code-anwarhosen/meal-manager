from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User


def register_user(request):
    if request.user.is_authenticated:
        messages.info(request, 'Already logged in!')
        return redirect('home')
    
    if request.method == 'POST':
        fullname = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm_password')
        
        context = {
            'fullname': fullname,
            'phone': phone,
            'email': email
        }
        
        # Validation
        errors = []
        
        if not phone or len(phone) < 3:
            errors.append('Phone number must be 11 characters.')
        
        if not password1 or len(password1) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password1 != password2:
            errors.append('Passwords do not match.')
        
        if User.objects.filter(username=phone).exists():
            errors.append('User with the phone number already exists.')
        
        if email and User.objects.filter(email=email).exists():
            errors.append('User with the email already exists.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'auth/register.html', context)
        
        try:
            user = User.objects.create_user(
                username=phone,
                email=email,
                first_name=fullname
            )
            user.set_password(password1)
            user.save()
            
            messages.success(request, 'Registration successful! You can now login now.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'auth/register.html', context)
    
    return render(request, 'auth/register.html')
    
    

def login_user(request):
    if request.user.is_authenticated:
        messages.info(request, 'Already logged in!')
        return redirect('home')
        
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        user = authenticate(username=phone, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Login successful!')
            
            # Check if user has group
            if hasattr(user, 'group_membership'):
                return redirect('home')
            
            # else:
            #     return redirect('setup-group')
            
            return redirect('home')
            
        else:
            messages.error(request, 'Invalid username or password!')
            return render(request, 'auth/login.html', {'phone': phone})
        
    return render(request, 'auth/login.html')


def logout_user(request):
    user = request.user
    
    if user:
        logout(request)
        messages.success(request, 'Logout success')
        
    return redirect('login')
