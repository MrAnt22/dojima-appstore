from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.shortcuts import redirect

def my_profile_redirect(request):
    if request.user.is_authenticated:
        return redirect('profile', username=request.user.username)
    else:
        # redirect to login or somewhere else if not logged in
        return redirect('login')

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('profile/', my_profile_redirect, name='my_profile_redirect'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('create-post/', views.create_post, name='create_post'),
    path('post/<str:post_type>/<int:post_id>/', views.post, name='post')
]
