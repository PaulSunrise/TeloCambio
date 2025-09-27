from django.urls import path, include
from . import views

urlpatterns = [
    # Autenticación
    path('auth/verify/', views.verify_registration, name='verify-registration'),
    path('auth/register/', views.user_register, name='user-register'),
    path('auth/login/', views.user_login, name='user-login'),
    path('auth/logout/', views.user_logout, name='user-logout'),
    path('auth/user/', views.current_user, name='current-user'),
    path('auth/token/refresh/', views.token_refresh, name='token-refresh'),
    
    # Gestión de usuarios (admin)
    path('users/', views.community_users_list, name='community-users'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle-user-status'),
    
    # Padrón de correos (admin) - URLS ACTUALIZADAS
    path('email-registry/', views.email_registry_list, name='email-registry-list'),
    path('email-registry/<int:email_id>/', views.email_registry_detail, name='email-registry-detail'),
    
    # Comunidades (solo superadmin)
    path('communities/', views.CommunityListAPIView.as_view(), name='community-list'),
]