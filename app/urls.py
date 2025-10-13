from django.urls import path
from django.contrib.auth import views as auth_views
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
    path('member-details/<int:member_pk>/', views.member_details, name='member-details'),
    path('create-grocery/<int:member_pk>/', views.create_grocery, name='create-grocery'),
    
    # Update things
    path('update-meal/<int:member_pk>/', views.update_meal, name='update-meal'),
    path('update-grocery/<int:member_pk>/', views.update_grocery, name='update-grocery'),
]

acc_related_urls = [
    path('account/', views.account, name='account'),
    path('delete-account/', views.delete_account, name='delete-account'),
    path('update-account/', views.update_account, name='update-account'),
    path('change-password/', views.change_password, name='change-password'),
]

forgot_pass_urls = [
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html'), 
        name='password_reset'
    ),
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), 
        name='password_reset_done'
    ),
    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), 
        name='password_reset_confirm'
    ),
    path('reset/done/', 
        auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), 
        name='password_reset_complete'
    ),
]
urlpatterns.extend(acc_related_urls)
urlpatterns.extend(forgot_pass_urls)
