from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from . import views

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
    path('post/<str:post_type>/<int:post_id>/', views.post, name='post'),
    path('delete-review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)