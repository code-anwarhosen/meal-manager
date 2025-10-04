from django.contrib import admin
from app.models import Group, GroupMember, MealEntry, GroceryExpense

admin.site.register(Group)
admin.site.register(GroupMember)
admin.site.register(MealEntry)
admin.site.register(GroceryExpense)
