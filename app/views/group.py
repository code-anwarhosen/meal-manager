from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from app.models import Group, GroupMember
from app.utils import group_required
from .helpers import get_member_details
from datetime import date


@login_required
def setup_group(request):
    """Main setup page - choose create or join"""
    # If user already has group, redirect to home
    if hasattr(request.user, 'group_membership'):
        return redirect('home')
    
    return render(request, 'group/setup_group.html')


@login_required
def create_group(request):
    """Create new group"""
    user = request.user
    
    # If user already has group, redirect to home
    if hasattr(user, 'group_membership'):
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


@login_required
@group_required
def leave_group(request):
    if request.method != 'POST':
        messages.error(request, "Invalid request method")
        return redirect('home')
    
    user = request.user
    member = user.group_membership
    group = member.group
    
    current_date = date.today()
    member = get_member_details(member, current_date.month, current_date.year)
    has_balance = member.balance < 0
    
    
    if group.members.count() == 1:
        # Only one member also means that he is admin, so safe to delete
        messages.info(request, "Group deleted, since you are the only member!")
        group.delete()
        
    elif user == group.admin:
        # Admin, group has more than one member
        if has_balance:
            messages.info(request, "You have unsettled balance. Settle the balance.")
        
        messages.info(request, "Transfer admin role to someone else to leave the group")
        
    else:
        # Members, more than one
        if has_balance:
            messages.info(request, f"You have unsettled balance. Settle the balance first!")
        
        else:
            messages.success(request, "Leaving the group!")
            member.delete()

    return redirect('home')
