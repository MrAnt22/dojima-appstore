from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

def home(request):
    # Dummy post data
    posts = [{
        "title": "SuperCoolApp",
        "description": "This is a very useful app that automates stuff and saves your time. Great for all users.",
        "rating": 4,
        "views": 1500,
        "likes": 215,
        "comments": 12,
        "timestamp": "May 20, 2025",
        "admin": {
            "username": "Admin #1",
            "avatar_url": "/static/img/admin.png"
        }
    },
    {
        "title": "Guide to WinRAR 2032",
        "description": "A deeply insightful, deeply cursed guide on how to survive the WinRAR trial popup apocalypse...",
        "rating": 5,
        "views": 420,
        "likes": 69,
        "comments": 7,
        "timestamp": "May 18, 2025",
        "admin": {
            "username": "evilsans123",
            "avatar_url": "/static/img/memez.png"
        }
    }]

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
