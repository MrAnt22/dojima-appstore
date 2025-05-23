from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import PostForm, ReviewForm
from .models import Post, Review
from django.core.paginator import Paginator


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
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form, 'show_navbar': False})

# Dummy model-like objects
class DummyPost:
    def __init__(self, id, title):
        self.id = id
        self.title = title

class DummyReview:
    def __init__(self, app_name, text):
        self.app_name = app_name
        self.text = text

class DummyRating:
    def __init__(self, app_name, value):
        self.app_name = app_name
        self.value = value

def profile(request, username):
    from collections import namedtuple

    User = namedtuple('User', ['uid', 'username', 'is_staff', 'avatar_url'])
    Post = namedtuple('Post', ['pid',  'user', 'title', 'description', 'rating', 'views', 'impressions', 'comments', 'timestamp'])
    Review = namedtuple('Review', ['rid', 'post', 'reviewer', 'comment', 'rating', 'timestamp'])
    Comment = namedtuple('Comment', ['cid', 'post', 'reviewer', 'text', 'timestamp'])

    profile_user = {
        'username': username,
        'date_joined': '2023-01-01',
        'profile': {'avatar_url': '/static/img/default-avatar.png'}
    }

    users = [
        User(1, "GOD_ADMIN_123", True, 'img/default-avatar.png')
    ]

    posts = [
        Post(1, users[0], 'Awesome App', 'This app rocks and helps a lot.', 5, 120, 45, 10, '2025-05-21 10:00'),
    ]

    reviews = [
        Review(1, posts[0], username, 'Great experience!', 5, '2025-05-21 10:00'),
    ]

    comments = [
        Comment(1, posts[0], username, 'I couldnt open the first link, any help?',  '2025-05-21 10:00'),
    ]

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'reviews': reviews,
        'comments': comments,
    })

@login_required
def settings_view(request):
  
    profile_user = {
        'username': "test",
        'date_joined': '2023-01-01',
        'profile': {'avatar_url': '/static/img/default-avatar.png'}
    }

    return render(request, 'settings.html', {'profile_user': profile_user})


def post(request, post_type, post_id):
    # ----- Real logic (commented out) -----
    # post = get_object_or_404(Post, id=post_id, type=post_type)
    # if post_type == 'app':
    #     files = AppFile.objects.filter(post=post)
    #     reviews = AppReview.objects.filter(post=post)
    #     avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    #     context = {'post': post, 'files': files, 'reviews': reviews, 'avg_rating': avg_rating}
    # else:
    #     comments = Comment.objects.filter(post=post)
    #     context = {'post': post, 'comments': comments}

    # ----- Dummy logic for frontend -----
    post = {
        'id': post_id,
        'type': post_type,
        'title': 'Dummy App Title',
        'description': 'This is a dummy description of an app post.',
        'user': {'username': 'testuser'},
        'views': 123,
        'likes': [1, 2, 3],  # pretend these are user IDs
        'categories': [{'name': 'Tools'}, {'name': 'Productivity'}],
        'timestamp': timezone.now(),
    }

    if post_type == 'app':
        files = [
            {'file': {'url': '/media/dummy1.zip', 'name': 'dummy1.zip'}},
            {'file': {'url': '/media/dummy2.zip', 'name': 'dummy2.zip'}},
        ]
        reviews = [
            {'user': {'username': 'alice'}, 'rating': 5, 'content': 'Amazing!', 'timestamp': timezone.now()},
            {'user': {'username': 'bob'}, 'rating': 4, 'content': 'Pretty good.', 'timestamp': timezone.now()},
        ]
        avg_rating = 4.5
        context = {'post': post, 'files': files, 'reviews': reviews, 'avg_rating': avg_rating}
    else:  # forum post
        comments = [
            {'user': {'username': 'alice'}, 'content': 'Great guide!', 'timestamp': timezone.now()},
            {'user': {'username': 'bob'}, 'content': 'Helped a lot.', 'timestamp': timezone.now()},
        ]
        context = {'post': post, 'comments': comments}

    return render(request, 'post.html', context)

@login_required
@user_passes_test(is_admin)
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES) 
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