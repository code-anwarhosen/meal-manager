from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date

from app.models import GroupMember, MealEntry
from app.utils import get_date, group_required
from .helpers import handle_add_update_meals, get_member_details, member_summary, group_summary


@login_required
@group_required
def home(request):
    user = request.user
    current_date = date.today()
    
    # get the group with needed attributes for dashboard 
    # group_summary(..) -> Group
    group = group_summary(
        group=user.group_membership.group, 
        month=current_date.month, 
        year=current_date.year
    )
    
    # list of all member of the group
    members_list = group.members.all().select_related('user')
    
    # add needed attributes for the dashboard to each member of the group
    # member: GroupMember
    for mem_idx in range(len(members_list)):
        
        total_meals, total_spent, *_ = member_summary(
            member=members_list[mem_idx],    # members_list[mem_idx]: GroupMember
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


@login_required
@group_required
def track_meals(request):
    user = request.user
    group = user.group_membership.group
    
    date_str = request.GET.get('date')
    direction = request.GET.get('dir')
    
    meal_date = get_date(date_str, direction)
    
    if meal_date > date.today():
        return redirect('track-meals')
    
    # handle create/update MealEntry
    if request.method == 'POST':
        handle_add_update_meals(request, group)
        
    
    # list of all member of the group
    members_list = group.members.all().select_related('user')
    
    # add needed attributes for the dashboard to each member of the group
    # member: GroupMember
    for mem_idx in range(len(members_list)):
        user = members_list[mem_idx].user
        meal = user.meal_entries.filter(date=meal_date).first()
        
        members_list[mem_idx].breakfast = meal.breakfast if meal else 0
        members_list[mem_idx].lunch = meal.lunch if meal else 0
        members_list[mem_idx].dinner = meal.dinner if meal else 0
    
    group.members_list = members_list
    
    context = {
        'group': group,
        'meal_date': meal_date,
    }
    return render(request, 'home/track_meals.html', context)


@login_required
@group_required
def member_details(request, member_pk):
    member = GroupMember.objects.filter(pk=member_pk).select_related('user').first()
    
    if not member:
        messages.error(request, 'Not a valid user/member!')
        return redirect('home')
    
    info_date = date.today()
    
    member = get_member_details(
        member,
        info_date.month,
        info_date.year
    )
    
    context = {
        'member': member,
        'info_date': info_date
    }
    return render(request, 'home/member_details.html', context)


@login_required
@group_required
def update_meal(request, member_pk):
    if request.method != 'POST':
        messages.error(request, "Invalid request method")
        return redirect('member-details', member_pk=member_pk)
    
    meal_id = request.POST.get('meal_id')
    breakfast = request.POST.get('breakfast', '0')
    lunch = request.POST.get('lunch', '0')
    dinner = request.POST.get('dinner', '0')
    
    # Validate meal_id exists
    if not meal_id:
        messages.error(request, "Meal ID is required")
        return redirect('member-details', member_pk=member_pk)
    
    # Convert values with better error handling
    try:
        meal_id = int(meal_id)
        breakfast = int(breakfast) if breakfast.strip() else 0
        lunch = int(lunch) if lunch.strip() else 0
        dinner = int(dinner) if dinner.strip() else 0
        
        # Validate non-negative values
        if any(val < 0 for val in [breakfast, lunch, dinner]):
            raise ValueError("Meal counts cannot be negative")
            
    except ValueError as e:
        messages.error(request, f"Invalid input: {e}")
        return redirect('member-details', member_pk=member_pk)
    
    # Get and validate meal
    try:
        meal = MealEntry.objects.get(pk=meal_id)
        
        # Verify if the user is the owner or group admin
        if meal.user != request.user and meal.group.admin != request.user:
            messages.error(request, "Permission denied")
            return redirect('member-details', member_pk=member_pk)
        
        meal.breakfast = breakfast
        meal.lunch = lunch
        meal.dinner = dinner
        meal.save()
        
        messages.success(request, "Meal updated successfully!")
        
    except MealEntry.DoesNotExist:
        messages.error(request, "Meal not found")
    except Exception as e:
        messages.error(request, f"Error updating meal: {str(e)}")
    
    return redirect('member-details', member_pk=member_pk)
