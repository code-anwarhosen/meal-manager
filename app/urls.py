from django.urls import path
from app import views

urlpatterns = [
    # auth views
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    
    # main views
    path('', views.home, name='home'),
]
