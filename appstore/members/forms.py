from django import forms
from .models import Post
from .models import Review

class PostForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('tools', 'App'),
        ('guides', 'Guide (Forum)'),
        ('announcements', 'Announcement (Forum)'),
    ]

    category = forms.ChoiceField(choices=CATEGORY_CHOICES, label='Post Type')

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'file']
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} ☆') for i in range(1, 6)]),
        }