from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date

from app.models import GroupMember, MealEntry, GroceryExpense
from app.utils import get_date, group_required
from .helpers import handle_add_update_meals, get_member_details, member_summary, group_summary


@login_required
@group_required
def home(request):
    user = request.user
    
    # Get Date
    date_str = request.GET.get('date')
    direction = request.GET.get('dir')
    current_date = get_date(date_str, direction, unit='month')
    
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
        members_list[mem_idx].total_cost = round(total_cost)
        members_list[mem_idx].total_spent = total_spent
        members_list[mem_idx].balance = round(total_spent - total_cost)
    
    # add members_list attribute to group 
    # to be able to access all memner of the group in template
    group.members_list = members_list
    
    context = {
        'group': group,
        'current_month': current_date
    }
    return render(request, 'home/dashboard.html', context)


@login_required
@group_required
def track_meals(request):
    user = request.user
    group = user.group_membership.group
    
    # Get Date
    date_str = request.GET.get('date')
    direction = request.GET.get('dir')
    meal_date = get_date(date_str, direction)
    
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
    
    # Get Date
    date_str = request.GET.get('date')
    direction = request.GET.get('dir')
    info_date = get_date(date_str, direction, unit='month')
    
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


@login_required
@group_required
def create_grocery(request, member_pk):
    if request.method != 'POST':
        messages.error(request, "Invalid request method")
        return redirect('member-details', member_pk=member_pk)
    
    # Extract and validate required fields
    grocery_date = request.POST.get('grocery_date', '').strip()
    item_name = request.POST.get('item_name', '').strip()
    quantity = request.POST.get('quantity', '').strip()
    cost = request.POST.get('cost', '0').strip()
    
    # Validate required fields
    if not grocery_date or not item_name:
        messages.error(request, "Date and Item Name are required")
        return redirect('member-details', member_pk=member_pk)
    
    try:
        # Validate and parse inputs
        grocery_date = date.fromisoformat(grocery_date)
        cost = int(cost) if cost else 0
        
        if cost < 0:
            messages.error(request, "Cost cannot be negative")
            return redirect('member-details', member_pk=member_pk)
            
        # Get member with related objects
        member = GroupMember.objects.select_related('user', 'group').get(pk=member_pk)
        
        # Check permissions
        if member.user != request.user and member.group.admin != request.user:
            messages.error(request, "Permission denied")
            return redirect('member-details', member_pk=member_pk)
        
        # Create grocery expense
        GroceryExpense.objects.create(
            user=member.user,
            group=member.group,
            date=grocery_date,
            item_name=item_name,
            quantity=quantity,
            cost=cost
        )
        messages.success(request, "Grocery item added successfully!")
        
    except ValueError as e:
        if "fromisoformat" in str(e):
            messages.error(request, "Invalid date format")
        else:
            messages.error(request, "Invalid cost value")
    except GroupMember.DoesNotExist:
        messages.error(request, "Member not found")
        return redirect('home')
    except Exception as e:
        messages.error(request, f"Error creating grocery item: {str(e)}")
    
    return redirect('member-details', member_pk=member_pk)


@login_required
@group_required
def update_grocery(request, member_pk):
    if request.method != 'POST':
        messages.error(request, "Invalid request method")
        return redirect('member-details', member_pk=member_pk)
    
    grocery_id = request.POST.get('grocery_id')
    item_name = request.POST.get('item_name')
    quantity = request.POST.get('quantity')
    cost = request.POST.get('cost', '0')
    
    # Validate meal_id exists
    if not grocery_id:
        messages.error(request, "Grocery ID is required")
        return redirect('member-details', member_pk=member_pk)
    
    # Convert values with better error handling
    try:
        grocery_id = int(grocery_id)
        cost = int(cost) if cost.strip() else 0
        
        # Validate non-negative values
        if cost < 0:
            raise ValueError("Cost cannot be negative")
            
    except ValueError as e:
        messages.error(request, f"Invalid input: {e}")
        return redirect('member-details', member_pk=member_pk)
    
    # Get and validate grocery
    try:
        grocery = GroceryExpense.objects.get(pk=grocery_id)
        
        # Verify if the user is the owner or group admin
        if grocery.user != request.user and grocery.group.admin != request.user:
            messages.error(request, "Permission denied")
            return redirect('member-details', member_pk=member_pk)
        
        grocery.item_name = item_name
        grocery.quantity = quantity
        grocery.cost = cost
        grocery.save()
        messages.success(request, "Grocery updated successfully!")
        
    except GroceryExpense.DoesNotExist:
        messages.error(request, "Grocery not found")
    except Exception as e:
        messages.error(request, f"Error updating grocery: {str(e)}")
    
    return redirect('member-details', member_pk=member_pk)
