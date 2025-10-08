from django.shortcuts import redirect
from datetime import date, timedelta


# Decorator
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


def get_date(date_str: str, direction: str, unit: str = 'day'): 
    """
    Args: 
        date_str: string in iso format e.g. yyyy-mm-dd
        direction: prev or next
        unit: day or month
    Return:
        class: datetime.date
    """
    try:
        current_date = date.fromisoformat(date_str)
    except Exception:
        current_date = date.today()
    
    if not direction in ['prev', 'next'] or not unit in ['day', 'month']:
        return current_date
        
    if unit == 'day':
        if direction == 'prev':
            return current_date - timedelta(days=1)
        
        elif direction == 'next':
            return current_date + timedelta(days=1)
    
    elif unit == 'month':
        year = current_date.year
        month = current_date.month
        
        if direction == 'prev':
            if month == 1:
                month, year = 12, year - 1
            else:
                month -= 1
        elif direction == 'next':
            if month == 12:
                month, year = 1, year + 1
            else:
                month += 1
        
        # Max days of month
        if month in [4, 6, 9, 11]:
            max_days = 30
        elif month == 2:
            # Future improvement, case: leap year
            max_days = 28
        else:
            max_days = 31
        
        # Get days of the month
        day = min(current_date.day, max_days)
        
        return date(year, month, day)
    
    return current_date
