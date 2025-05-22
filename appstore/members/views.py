from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import PostForm, ReviewForm
from .models import Post, Review


def is_admin(user):
    return user.is_staff

def home(request):
    # # Dummy post data
    # posts = [{    
    #     "title": "SuperCoolApp",
    #     "description": "This is a very useful app that automates stuff and saves your time. Great for all users.",
    #     "rating": 4,
    #     "views": 1500,
    #     "likes": 215,
    #     "comments": 12,
    #     "timestamp": "May 20, 2025",
    #     "admin": {
    #         "username": "Admin #1",
    #         "avatar_url": "/static/img/admin.png"
    #     }
    # },
    # {
    #     "title": "Guide to WinRAR 2032",
    #     "description": "A deeply insightful, deeply cursed guide on how to survive the WinRAR trial popup apocalypse...",
    #     "rating": 5,
    #     "views": 420,
    #     "likes": 69,
    #     "comments": 7,
    #     "timestamp": "May 18, 2025",
    #     "admin": {
    #         "username": "evilsans123",
    #         "avatar_url": "/static/img/memez.png"
    #     }
    # }]

    # return render(request, 'home.html', {'posts': posts})
    posts = Post.objects.all().order_by('-created_at')  # Show newest first
    return render(request, 'home.html', {'posts': posts})

def search(request):
    return render(request, 'search.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def settings_view(request):
    return render(request, 'settings.html')

@login_required
@user_passes_test(is_admin)
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'create-post.html', {'form': form})

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
    })