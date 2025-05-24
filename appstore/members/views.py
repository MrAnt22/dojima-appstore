from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db.models import Avg
from .forms import PostForm, ReviewForm
from .models import Category, Post, Review, Comment, AppFile

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
    profile_user = get_object_or_404(User, username=request.user)
    
    if request.method == 'POST':
        new_username = request.POST.get('username', '').strip()
        if not new_username:
            messages.error(request, "Username cannot be blank.")
        elif User.objects.exclude(pk=request.user.pk).filter(username=new_username).exists():
            messages.error(request, "That username is already taken.")
        else:
            request.user.username = new_username
            request.user.save()
            messages.success(request, "Username updated successfully.")
            return redirect('settings')

    return render(request, 'settings.html', { 
        'profile_user': profile_user,
        'show_navbar': True,
    })

def post(request, post_type, post_id):
    post = get_object_or_404(Post, id=post_id, type=post_type)

    if request.method == 'POST' and request.user.is_authenticated:
        if post_type == 'app':
            
            rating = request.POST.get('rating')
            content = request.POST.get('content')
            if rating and content:
                existing_review = Review.objects.filter(post=post, user=request.user).first()
                if existing_review:
                    messages.error(request, "You’ve already reviewed this app.")
                else:
                    Review.objects.create(post=post, user=request.user, rating=rating, content=content)
                    messages.success(request, "Your review has been submitted.")
                    return redirect('post', post_type=post_type, post_id=post.id)

        elif post_type == 'post':
            
            content = request.POST.get('content')
            if content:
                Comment.objects.create(post=post, user=request.user, content=content)
                messages.success(request, "Your comment has been added.")
                return redirect('post', post_type=post_type, post_id=post.id)

    if post_type == 'app':
        files = AppFile.objects.filter(post=post)
        reviews = Review.objects.filter(post=post)
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        context = {
            'post': post,
            'files': files,
            'reviews': reviews,
            'avg_rating': avg_rating,
            'show_navbar': True
        }
    else:
        comments = Comment.objects.filter(post=post)
        context = {
            'post': post,
            'comments': comments,
            'show_navbar': True
        }

    return render(request, 'post.html', context)

@login_required
@user_passes_test(is_admin)
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    post_url = review.post.get_absolute_url()
    review.delete()
    messages.success(request, "Review deleted successfully.")
    return redirect(post_url)

@login_required
@user_passes_test(is_admin)
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_url = comment.post.get_absolute_url()
    comment.delete()
    messages.success(request, "Comment deleted successfully.")
    return redirect(post_url)

@login_required
@user_passes_test(is_admin)
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        files = request.FILES.getlist('files') 
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            form.save_m2m()

            for uploaded_file in files:
                AppFile.objects.create(post=post, file=uploaded_file)

            return redirect('home')
    else:
        form = PostForm()

    categories = Category.objects.all()
    context = {
        'form': form,
        'categories': categories,
        'show_navbar': True
    }
    return render(request, 'create-post.html', context)
