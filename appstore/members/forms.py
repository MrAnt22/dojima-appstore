from django import forms
from .models import Post, Review, Comment, AppFile, Category

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'type', 'categories']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'categories': forms.CheckboxSelectMultiple(),
        }


class AppFileForm(forms.ModelForm):
    class Meta:
        model = AppFile
        fields = ['file']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Write your comment...'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']