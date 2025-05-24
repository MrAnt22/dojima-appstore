import os
import django
import json
import re
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', config('DJANGO_SETTINGS_MODULE'))
django.setup()

from django.contrib.auth import get_user_model
from members.models import Post
from django.utils.text import slugify
from members.models import Post

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

        slug = latin_underscore_slug(title)
        slug_unique = generate_unique_slug(slug)
        post_type = Post.APP if files else Post.POST

        post = Post.objects.create(
            user=user,
            title=title,
            description=description,
            views=views,
            type=post_type,
            slug=slug_unique,
        )

        print(f"Created {post_type} post '{title}' with slug '{slug}'")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python import_posts.py path/to/cleaned.json")
        sys.exit(1)

    json_file = sys.argv[1]
    run(json_file)
