from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.models import Group, GroupMember


@login_required
def setup_group(request):
    """Main setup page - choose create or join"""
    user = request.user
    
    # If user already has group, redirect to home
    if hasattr(user, 'group_membership'):
        messages.info(request, 'You already have a group!')
        return redirect('home')
    
    return render(request, 'group/setup_group.html')


@login_required
def create_group(request):
    """Create new group"""
    user = request.user
    
    # If user already has group, redirect to home
    if hasattr(user, 'group_membership'):
        messages.info(request, 'You already have a group!')
        return redirect('home')
    
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        description = request.POST.get('description')
        
        if group_name:
            # Create group (join_code auto-generated in model)
            Group.objects.create(
                name=str(group_name).strip(), 
                description=str(description).strip() if description else None, 
                admin=user
            )
            
            messages.success(request, f'Group "{group_name}" created successfully!')
            return redirect('home')
        
        else:
            messages.error(request, 'Group name is required')
    
    return redirect('setup-group')


@login_required
def join_group(request):
    """Join existing group with code"""
    user = request.user
    
    if hasattr(user, 'group_membership'):
        messages.info(request, 'You already have a group!')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            join_code = request.POST.get('join_code', '').strip().upper()
        
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
    
    return redirect('setup-group')
