from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_developer = models.BooleanField(default=False)

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('tools', 'Tools'),
        ('guides', 'Guides'),
        ('announcements', 'Announcements'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    rating = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    file = models.FileField(upload_to='uploads/', null=True, blank=True)

    def update_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            self.rating = round(sum(r.rating for r in reviews) / reviews.count(), 1)
        else:
            self.rating = 0
        self.save()

    def __str__(self):
        return self.title
    
class Review(models.Model):
    post = models.ForeignKey(Post, related_name='reviews', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Post(models.Model):
    POST_TYPES = [
        ('app', 'App'),
        ('forum', 'Forum'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=10, choices=POST_TYPES)
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, related_name='posts', blank=True)

    def __str__(self):
        return f"[{self.type}] {self.title}"

class AppFile(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='apps/')

    def __str__(self):
        return self.file.name

class AppReview(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} - {self.rating}/5"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username}"
