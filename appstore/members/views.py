from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db.models import Avg, Q
from .forms import CustomUserCreationForm, PostForm
from .models import Category, Post, Profile, Review, Comment, AppFile

def is_admin(user):
    return user.is_staff

def home(request):
    categories = Category.objects.all().order_by('name')
    query = request.GET.get('q', '')
    selected_categories = request.GET.getlist('category')

    posts = Post.objects.all()

    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if selected_categories:
        posts = posts.filter(categories__id__in=selected_categories)

    posts = posts.order_by('-created')

    paginator = Paginator(posts, 3) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', {
        'page_obj': page_obj,
        'show_navbar': True,
        'query': query,
        'categories': categories,
        'selected_categories': list(map(int, selected_categories)),
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # creates User and saves it
            avatar = form.cleaned_data.get('avatar')

            if avatar:
                # Create profile or use the signal, then save avatar
                user.profile.avatar = avatar
                user.profile.save()

            return redirect('login')
        else:
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form, 'show_navbar': False})

def about_us(request):
    return render(request, 'about-us.html', {'show_navbar': True})

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
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        new_username = request.POST.get('username', '').strip()
        avatar = request.FILES.get('avatar')

        if not new_username:
            messages.error(request, "Username cannot be blank.")
        elif User.objects.exclude(pk=request.user.pk).filter(username=new_username).exists():
            messages.error(request, "That username is already taken.")
        else:
            request.user.username = new_username
            request.user.save()
            messages.success(request, "Username updated successfully.")

        if avatar:
            profile.avatar = avatar
            profile.save()
            messages.success(request, "Avatar updated successfully.")

        return redirect('settings')

    context = {
        'profile_user': request.user,
        'show_navbar': True,
    }
    return render(request, 'settings.html', context)


def post(request, post_type, post_id):
    post = get_object_or_404(Post, id=post_id, type=post_type)

    session_key = f'post/{post.type}/{post.id}'
    if not request.session.get(session_key, False):
        post.views += 1
        post.save()
        request.session[session_key] = True

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
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    post_url = review.post.get_absolute_url()

    if request.user.is_superuser or review.user == request.user:
        review.delete()
        messages.success(request, "Review deleted successfully.")
    else:
        messages.error(request, "You don't have permission to delete this review.")

    return redirect(post_url)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_url = comment.post.get_absolute_url()

    if request.user.is_superuser or comment.user == request.user:
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You don't have permission to delete this comment.")

    return redirect(post_url)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user.is_superuser or post.user == request.user:
        post.delete()
        messages.success(request, "Post deleted successfully.")
    else:
        messages.error(request, "You don't have permission to delete this post.")
        return redirect(post.get_absolute_url())

    return redirect('home')

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


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'home'))
