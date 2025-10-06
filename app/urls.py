from django.urls import path
from app import views

urlpatterns = [
    # Auth Views
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    
    # Group Views
    path('setup-group/', views.setup_group, name='setup-group'),
    path('create-new-group/', views.create_group, name='create-group'),
    path('join-existing-group/', views.join_group, name='join-group'),
    
    # Main App (Protected) 
    path('', views.home, name='home'),
    path('track-meals/', views.track_meals, name='track-meals'),
]
