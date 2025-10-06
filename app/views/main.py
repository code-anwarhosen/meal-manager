from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.models import GroupMember, MealEntry
from app.utils import group_required, group_summary, member_summary
from datetime import date, timedelta


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


def handle_add_update_meals(request, group):
    date_str = request.POST.get('meal_date')
    
    if not date_str:
        messages.error(request, 'Date is required')
        return redirect('track-meals')
    
    try:
        # Get all members in the group
        members = GroupMember.objects.filter(group=group)
        
        # track if creating or updating
        is_new_entry = False
        
        # Process each member's meal data
        for member in members:
            breakfast = request.POST.get(f'member_{member.pk}_breakfast')
            lunch = request.POST.get(f'member_{member.pk}_lunch')
            dinner = request.POST.get(f'member_{member.pk}_dinner')
            
            # Convert to integers with validation
            try:
                breakfast_int = int(breakfast) if breakfast else 0
                lunch_int = int(lunch) if lunch else 0
                dinner_int = int(dinner) if dinner else 0
                
                # Validate within range (0-3 as per model)
                breakfast_int = max(0, min(3, breakfast_int))
                lunch_int = max(0, min(3, lunch_int))
                dinner_int = max(0, min(3, dinner_int))
                
            except ValueError:
                messages.error(request, 'Invalid meal value. Please enter numbers only.')
                return redirect('track-meals')
            
            # update_or_create with defaults parameter
            _, is_new_entry = MealEntry.objects.update_or_create(
                user=member.user,
                group=group,
                date=date_str,
                defaults={
                    'breakfast': breakfast_int,
                    'lunch': lunch_int,
                    'dinner': dinner_int,
                }
            )
        
        action = 'added' if is_new_entry else 'updated'
        messages.success(request, f'Meal entries {action} for {date_str}')
        return redirect('track-meals')
        
    except Exception as e:
        messages.error(request, f'Error saving meals: {str(e)}')
        return redirect('track-meals')


def get_meal_date(request):
    date_str = request.GET.get('date')
    
    meal_date = date.today()
    try:
        meal_date = date.fromisoformat(date_str)
    except Exception as e:
        pass
    
    dir = request.GET.get('dir')
    one_day = timedelta(days=1)
    
    if dir == 'back':
        meal_date = meal_date - one_day
    elif dir == 'forward':
        meal_date = meal_date + one_day
        
    return meal_date
    

@login_required
@group_required
def track_meals(request):
    user = request.user
    group = user.group_membership.group
    
    meal_date = get_meal_date(request)
    if meal_date > date.today():
        messages.info(request, "Can't access future date!")
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
