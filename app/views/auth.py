from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def register_user(request):
    if request.user.is_authenticated:
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
        return redirect('home')
        
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        user = authenticate(username=phone, password=password)
        if user:
            login(request, user)
            
            # Check if user has group
            if hasattr(user, 'group_membership'):
                return redirect('home')
            
            else:
                return redirect('setup-group')
            
        else:
            messages.error(request, 'Invalid username or password!')
            return render(request, 'auth/login.html', {'phone': phone})
        
    return render(request, 'auth/login.html')


def logout_user(request):
    user = request.user
    
    if user:
        logout(request)
        
    return redirect('login')

@login_required
def account(request):
    return render(request, 'auth/account.html')


@login_required
def update_account(request):
    if request.method != 'POST':
        messages.error(request, "Invalid request method")
        return redirect('account')
    
    full_name = request.POST.get('full_name')
    email = request.POST.get('email')
    
    if not full_name or not email:
        messages.error(request, f"full_name and email required!")
        return redirect('account')
    
    user = request.user
    try:
        user.first_name = full_name
        user.email = email
        user.save()
        messages.success(request, "Account update successful")
    except Exception as e:
        messages.error(request, f"Error: {e}")
        
    return redirect('account')


@login_required
def change_password(request):
    if request.method != 'POST':
        messages.error(request, "Invalid request method")
        return redirect('account')
    
    current_password = request.POST.get('current_password')
    new_password = request.POST.get('new_password')
    confirm_new_password = request.POST.get('confirm_new_password')
    
    if not current_password or not new_password or not confirm_new_password:
        messages.error(request, 'Current password, new password and confirm new password are required')
        return redirect('account')
    
    if new_password != confirm_new_password:
        messages.error(request, 'New password and confirm new password doesn\'t match')
        return redirect('account')
    if len(new_password) < 6:
        messages.error(request, 'New password must be at least 6 charecters')
        return redirect('account')
    
    user = request.user
    checked = user.check_password(current_password)
    
    if checked:
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request=request, user=user)
        messages.success(request, 'Password update successful')
    else:
        messages.error(request, 'Incorrect Password')
    
    return redirect('account')


@login_required
def delete_account(request):
    if request.method != 'POST':
        messages.error(request, "Invalid request method")
        return redirect('account')
    
    user = request.user
    
    # If not a member of a group, delete right away
    if not hasattr(user, 'group_membership'):
        user.delete()
        messages.success(request, "Account Delete - Done")
    
    else:
        group = user.group_membership.group
        role = 'admin' if group.admin == user else 'member'
        messages.info(request, f"You're '{role}' of '{group.name}'. Leave the group to delete your account.")
        
    return redirect('account')
