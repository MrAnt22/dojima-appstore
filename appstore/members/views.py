from datetime import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import PostForm, ReviewForm
from .models import Post, Review, Comment, AppFile
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db.models import Avg


def is_admin(user):
    return user.is_staff

def home(request):
    posts = Post.objects.all().order_by('-created')
    return render(request, 'home.html', {'posts': posts, 'show_navbar': True})

def search(request):
    return render(request, 'search.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form, 'show_navbar': False})

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    posts = Post.objects.filter(user=profile_user).order_by('-created')
    reviews = Review.objects.filter(user=profile_user).order_by('-created')
    comments = Comment.objects.filter(user=profile_user).order_by('-created')

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'reviews': reviews,
        'comments': comments,
        'show_navbar': True
    })

@login_required
def settings_view(request):
  
    profile_user = {
        'username': "test",
        'date_joined': '2023-01-01',
        'profile': {'avatar_url': '/static/img/default-avatar.png'}
    }

    return render(request, 'settings.html', {'profile_user': profile_user, 'show_navbar': True})

def post(request, post_type, post_id):
    post = get_object_or_404(Post, id=post_id, type=post_type)
    
    if post_type == 'app':
        files = AppFile.objects.filter(post=post)
        reviews = Review.objects.filter(post=post)
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        context = {'post': post, 'files': files, 'reviews': reviews, 'avg_rating': avg_rating, 'show_navbar': True}
    else:
        comments = Comment.objects.filter(post=post)
        context = {'post': post, 'comments': comments, 'show_navbar': True}

    return render(request, 'post.html', context)

@login_required
@user_passes_test(is_admin)
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            form.save_m2m()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, "create-post.html", {"form": form, 'show_navbar': True})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    reviews = post.reviews.all()
    form = ReviewForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.post = post
        review.author = request.user
        review.save()
        post.update_rating()
        return redirect('post_detail', pk=post.pk)

    return render(request, 'post_detail.html', {
        'post': post,
        'reviews': reviews,
        'form': form,
        'show_navbar': True
    })

def app_posts(request):
    posts = Post.objects.filter(category='tools').order_by('-created_at')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'post_app.html', {'page_obj': page_obj})

def forum_posts(request):
    posts = Post.objects.exclude(category='tools').order_by('-created_at')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'post_forum.html', {'page_obj': page_obj})

def post_app_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, category='tools')
    return render(request, 'post_detail.html', {'post': post})

def post_forum_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.category not in ['guides', 'announcements']:
        return redirect('home')
    return render(request, 'post_detail.html', {'post': post})
