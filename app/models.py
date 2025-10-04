from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import secrets


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    join_code = models.CharField(max_length=7, unique=True)
    admin = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_group')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.join_code:
            # Generate a unique 6-character join code
            self.join_code = self.generate_join_code()
        super().save(*args, **kwargs)
    
    def generate_join_code(self):
        """Generate a random 6-character join code"""
        while True:
            code = secrets.token_hex(3).upper()  # 6 characters
            if not Group.objects.filter(join_code=code).exists():
                return code
    
    def __str__(self):
        return self.name


class GroupMember(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='group_membership')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.role})"


class MealEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_entries')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='meal_entries')
    date = models.DateField()
    breakfast = models.IntegerField(default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(3)], 
        help_text="Number of breakfast meals (0=absent, 1=present, 2+=with guests)"
    )
    lunch = models.IntegerField(default=0,
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="Number of lunch meals (0=absent, 1=present, 2+=with guests)"
    )
    dinner = models.IntegerField(default=0,
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="Number of dinner meals (0=absent, 1=present, 2+=with guests)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'group', 'date']
        ordering = ['-date', 'user']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['group', 'date']),
        ]
    
    def total_meals(self):
        """Calculate total meals for the day"""
        return self.breakfast + self.lunch + self.dinner
    
    def cost(self, meal_rate: float):
        """Calculate cost for this meal entry"""
        return self.total_meals() * meal_rate
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.total_meals()} meals"


class GroceryExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grocery_expenses')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='grocery_expenses')
    
    date = models.DateField()
    item_name = models.CharField(max_length=200)
    quantity = models.CharField(max_length=50, blank=True, help_text="e.g., 2 kg, 1 packet, 5 pieces")
    cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['group', 'date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.item_name} - ₹{self.cost}"


# class MonthlySummary(models.Model):
#     """Optional: Pre-calculated monthly summaries for performance"""
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monthly_summaries')
#     group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='monthly_summaries')
#     year = models.IntegerField()
#     month = models.IntegerField()  # 1-12
#     total_meals = models.IntegerField(default=0)
#     total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
#     class Meta:
#         unique_together = ['user', 'group', 'year', 'month']
#         ordering = ['-year', '-month']
            
#     def __str__(self):
#         return f"{self.user.username} - {self.year}-{self.month:02d}"


# Signals to automatically create/update related records
from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=Group)
def create_admin_membership(sender, instance, created, **kwargs):
    """Automatically add admin as a group member when group is created"""
    if created:
        GroupMember.objects.create(
            user=instance.admin,
            group=instance,
            role='admin'
        )
