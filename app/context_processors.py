from app.models import GroupMember


def group_context(request):
    context = {}
    
    if request.user.is_authenticated:
        # Safe way to check and get group
        try:
            context['group'] = request.user.group_membership.group
            context['is_group_admin'] = request.user.group_membership.role == 'admin'
            
        except (GroupMember.DoesNotExist, AttributeError):
            # User has no group membership
            context['group'] = None
            context['is_group_admin'] = False
    
    return context
