from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # Profile endpoints
    path('profile/me/', views.get_current_user, name='get_current_user'),
    path('profile/', views.get_profile, name='get_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/<int:user_id>/', views.get_user_profile, name='get_user_profile'),
    
    # Follow endpoints
    path('follow/<int:user_id>/', views.toggle_follow, name='toggle_follow'),
    
    # Video endpoints
    path('videos/upload/', views.upload_video, name='upload_video'),
    path('videos/<int:video_id>/', views.get_video, name='get_video'),
    path('videos/user/<int:user_id>/', views.get_user_videos, name='get_user_videos'),
    
    # Inbox endpoints
    path('inbox/', views.get_inbox, name='get_inbox'),
    
    # Shop endpoints
    path('shop/<int:user_id>/', views.get_user_shop_items, name='get_user_shop_items'),
]

