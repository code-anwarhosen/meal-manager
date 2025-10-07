from django.db.models import Sum
from django.shortcuts import redirect
from app.models import MealEntry, GroceryExpense


def member_summary(member, group, month, year):
    """Calculate monthly summary of a group member"""
    
    meals_list = MealEntry.objects.filter(
        user=member.user,
        group=group,
        date__year=year,
        date__month=month
    )
    
    groceries_list = GroceryExpense.objects.filter(
        user=member.user,
        group=group,
        date__year=year,
        date__month=month
    )
    
    # Calculate meal totals
    total_meals = sum(meal.total for meal in meals_list)
    
    # Calculate spending
    total_spent = groceries_list.aggregate(Sum('cost'))['cost__sum'] or 0
    
    return total_meals, total_spent, meals_list, groceries_list


def group_summary(group, month: int, year: int):
    """Calculate monthly summary of a group"""
    
    group_groceries = GroceryExpense.objects.filter(
        group=group,
        date__year=year,
        date__month=month
    )
    group_meals = MealEntry.objects.filter(
        group=group,
        date__year=year,
        date__month=month
    )
    
    total_group_expenses = group_groceries.aggregate(Sum('cost'))['cost__sum'] or 0
    total_group_meals = sum(meal.total for meal in group_meals)
    
    # Calculate cost per meal (avoid division by zero)
    cost_per_meal = (total_group_expenses / total_group_meals) if total_group_meals > 0 else 0
    
    # Adding attributes to access in dashboard templates
    group.total_expenses = total_group_expenses
    group.total_meals = total_group_meals
    group.cost_per_meal = round(cost_per_meal, 2)
    
    return group


def group_required(view_func):
    """
    Decorator to check if user has a group
    Redirects to setup page if no group
    """
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'group_membership'):
            return redirect('setup-group')
        
        return view_func(request, *args, **kwargs)
    return wrapper
