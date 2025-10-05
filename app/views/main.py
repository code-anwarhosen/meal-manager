from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.utils import group_required, group_summary, member_summary
from datetime import datetime


@login_required
@group_required
def home(request):
    # Check if user has group
    user = request.user
    current_date = datetime.now()
    
    # get the group with needed attributes for dashboard 
    group = group_summary(
        group=user.group_membership.group, 
        month=current_date.month, 
        year=current_date.year
    )
    
    # list of all member of the group
    members_list = group.members.all().select_related('user')
    
    # add needed attributes in the dashboard for each member of the group
    # member: GroupMember
    for mem_idx in range(len(members_list)):
        
        total_meals, total_spent = member_summary(
            user=members_list[mem_idx].user,    # members_list[mem_idx]: GroupMember
            group=group, 
            month=current_date.month, 
            year=current_date.year
        )
        
        # group.cost_per_meal attribute added in the group_summary(..) -> Group
        total_cost = total_meals * group.cost_per_meal
        
        members_list[mem_idx].total_meals = total_meals
        members_list[mem_idx].total_cost = total_cost
        members_list[mem_idx].total_spent = total_spent
        members_list[mem_idx].balance = total_spent - total_cost
    
    # add members_list attribute to group 
    # to be able to access all memner of the group in template
    group.members_list = members_list
    
    context = {
        'group': group,
        'current_month': current_date.strftime('%B %Y')
    }
    return render(request, 'home/dashboard.html', context)
