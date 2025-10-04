from django.urls import path
from app import views

urlpatterns = [
    # auth views
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    
    # main views
    path('', views.home, name='home'),
    
    # group
    path('setup-group/', views.setup_group, name='setup-group'),
    path('create-new-group/', views.create_group, name='create-group'),
    path('join-existing-group/', views.join_group, name='join-group'),
]
