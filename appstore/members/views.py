from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

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
