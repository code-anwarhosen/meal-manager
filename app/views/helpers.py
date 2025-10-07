from django.contrib import messages
from django.shortcuts import redirect
from datetime import date, timedelta

from app.utils import group_summary, member_summary
from app.models import GroupMember, MealEntry


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


def get_member_details(member, month: int, year: int):
    # Get the total meals and spending of a member/user
    total_meals, total_spent, meals_list, grocery_list = member_summary(
        member=member,
        group=member.group,
        month=month, 
        year=year
    )
    
    # calling group_summary(..) -> Group, just to get the cost per meal
    group = group_summary(
        group=member.group, 
        month=month, 
        year=year
    )
    # group.cost_per_meal attribute added in the group_summary(..) -> Group
    total_cost = total_meals * group.cost_per_meal
    
    
    # Adding attributes directly to member: GroupMember 
    # for easy access in member details page
    member.total_meals = total_meals
    member.total_spent = total_spent
    member.total_cost = total_cost
    member.balance = total_spent - total_cost
    
    
    # Include all the meals and groceries of the given month to the member
    member.meals_list = meals_list
    member.groceries_list = grocery_list
    
    # Include meals summary
    member.months_total_breakfast = sum(meal.breakfast for meal in meals_list)
    member.months_total_lunch = sum(meal.lunch for meal in meals_list)
    member.months_total_dinner = sum(meal.dinner for meal in meals_list)
    
    return member
