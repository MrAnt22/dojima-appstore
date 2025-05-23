from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('create-post/', views.create_post, name='create_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/app/<int:pk>/', views.post_app_detail, name='post_app_detail'),
    path('post/forum/<int:pk>/', views.post_forum_detail, name='post_forum_detail'),
    path('post/app/', views.app_posts, name='app_posts'),
    path('post/forum/', views.forum_posts, name='forum_posts'),
]
