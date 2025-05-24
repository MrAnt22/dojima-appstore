import os
import django
import json
import re
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', config('DJANGO_SETTINGS_MODULE'))
django.setup()

from django.contrib.auth import get_user_model
from django.utils.text import slugify
from members.models import Post, AppFile, Category

User = get_user_model()

def generate_unique_slug(title):
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    while Post.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

def latin_underscore_slug(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    text = text.strip('_')
    
    return text[:140]

def run(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        posts_data = json.load(f)

    user = User.objects.filter(is_superuser=True).first()
    if not user:
        raise Exception("No superuser found in DB")

    for item in posts_data:
        title = item.get('title', '').strip()
        description = item.get('description', '').strip()
        views = item.get('views', 0)
        files = item.get('files', [])
        likes = item.get('likes', 0)
        created = item.get('created', 0)
        updated = item.get('updated', 0)

        slug = latin_underscore_slug(title)
        slug_unique = generate_unique_slug(slug)
        post_type = Post.APP if files else Post.POST

        category_name = 'App' if post_type == Post.APP else 'Post'
        category = Category.objects.get(name=category_name)

        post = Post.objects.create(
            user=user,
            title=title,
            description=description,
            views=views,
            created=created,
            updated=updated,
            telegram_like_count=likes,
            type=post_type,
            slug=slug_unique,
        )

        post.categories.add(category)

        for file_path in files:
            relative_path = os.path.relpath(file_path, 'appstore/media')
            AppFile.objects.create(
                post=post,
                file=relative_path
            )
            print(f"  -> Linked file: {relative_path}")

        print(f"Created {post_type} post '{title}' with slug '{slug}'")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python import_posts.py path/to/cleaned.json")
        sys.exit(1)

    json_file = sys.argv[1]
    run(json_file)
