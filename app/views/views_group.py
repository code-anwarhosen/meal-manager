from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.models import Group, GroupMember


@login_required
def setup_group(request):
    """Main setup page - choose create or join"""
    
    # If user already has group, redirect to home
    if hasattr(request.user, 'group_membership'):
        messages.info(request, 'You already have a group!')
        return redirect('home')
    
    return render(request, 'setup-group.html')


@login_required
def create_group(request):
    """Create new group"""
    user = request.user
    
    if hasattr(user, 'group_membership'):
        messages.info(request, 'You already have a group!')
        return redirect('home')
    
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        
        if group_name:
            # Create group (join_code auto-generated in model)
            group = Group.objects.create(name=group_name, admin=user)
            
            # add the user to the member list also
            GroupMember.objects.create(user=group.admin, group=group, role='admin')
            
            messages.success(request, f'Group "{group_name}" created successfully!')
            return redirect('home')
        
        else:
            messages.error(request, 'Group name is required')
    
    return render(request, 'create-group.html')


@login_required
def join_group(request):
    """Join existing group with code"""
    user = request.user
    
    if hasattr(user, 'group_membership'):
        messages.info(request, 'You already have a group!')
        return redirect('home')
    
    if request.method == 'POST':
        join_code = request.POST.get('join_code', '').strip().upper()
        
        try:
            group = Group.objects.get(join_code=join_code)
            
            # Add user as member
            GroupMember.objects.create(
                user=user,
                group=group,
                role='member'
            )
            
            messages.success(request, f'Joined to "{group.name}" successfully!')
            return redirect('home')
            
        except Group.DoesNotExist:
            messages.error(request, 'Invalid join code')
    
    return render(request, 'join-group.html')
