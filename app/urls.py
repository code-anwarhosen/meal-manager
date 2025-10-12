from django.urls import path
from app import views

urlpatterns = [
    # Auth Views
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    
    path('account/', views.account, name='account'),
    path('delete-account/', views.delete_account, name='delete-account'),
    path('update-account/', views.update_account, name='update-account'),
    path('change-password/', views.change_password, name='change-password'),
    
    # Group Views
    path('setup-group/', views.setup_group, name='setup-group'),
    path('create-new-group/', views.create_group, name='create-group'),
    path('join-existing-group/', views.join_group, name='join-group'),
    
    # Main App (Protected) 
    path('', views.home, name='home'),
    path('track-meals/', views.track_meals, name='track-meals'),
    path('member-details/<int:member_pk>/', views.member_details, name='member-details'),
    path('create-grocery/<int:member_pk>/', views.create_grocery, name='create-grocery'),
    
    # Update things
    path('update-meal/<int:member_pk>/', views.update_meal, name='update-meal'),
    path('update-grocery/<int:member_pk>/', views.update_grocery, name='update-grocery'),
]
