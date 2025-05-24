from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse
import os

User = get_user_model()

def generate_unique_slug(instance, base_slug):
    slug = base_slug
    num = 1
    while instance.__class__.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{num}"
        num += 1
    return slug

class TimestampedModel(models.Model):
    """Abstract base class that adds created/updated timestamps to models."""

    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
        ordering = ("-created",)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = self.created or timezone.now()
        self.updated = timezone.now()
        super().save(*args, **kwargs)


class Profile(TimestampedModel):
    """Extends the default Django user with extra profile information."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/img/default-avatar.png'

    def __str__(self):
        return f"Profile({self.user.username})"


class Category(models.Model):
    """Simple tagged category for grouping posts/apps."""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ("name",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(TimestampedModel):
    """Represents either a generic post/article or an application listing."""

    POST = "post"
    APP = "app"
    TYPE_CHOICES = [
        (POST, "Post"),
        (APP, "Application"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    telegram_like_count = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=120)
    description = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=POST)

    categories = models.ManyToManyField(Category, blank=True, related_name="posts")
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")

    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta(TimestampedModel.Meta):
        pass

    def __str__(self):
        return self.title
    
    def total_likes(self):
        return self.likes.count() + self.telegram_like_count

    # Convenience helpers --------------------------------------------------
    @property
    def average_rating(self):
        """Average of related review ratings, cached at runtime."""
        agg = self.reviews.aggregate(avg=models.Avg("rating"))
        return (agg["avg"] or 0)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = generate_unique_slug(self, base_slug)
        print(self.slug)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_type': self.type, 'post_id': self.id})
    
    def delete(self, *args, **kwargs):
        
        if self.files:
            if hasattr(self.files, 'all'):
                for file in self.files.all():
                    file_path = file.file.path
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    file.delete()
            else:
                file_path = self.files.path
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        super().delete(*args, **kwargs)

class AppFile(models.Model):
    """Binary files associated with an application‑type Post."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="files/")

    def __str__(self):
        return self.file.name


class Review(TimestampedModel):
    """User review with rating and text attached to an application post."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    content = models.TextField()

    class Meta(TimestampedModel.Meta):
        unique_together = ("post", "user")

    def __str__(self):
        return f"{self.user} › {self.post} ({self.rating}★)"


class Comment(TimestampedModel):
    """Comment on a post, used when the post is not an application."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()

    class Meta(TimestampedModel.Meta):
        ordering = ("created",)

    def __str__(self):
        return f"Comment({self.user} on {self.post})"
