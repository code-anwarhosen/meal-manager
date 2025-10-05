from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    # Check if user has group
    user = request.user
    
    if not hasattr(user, 'group_membership'):
        return redirect('setup-group')
            
    return render(request, 'home/home.html')
