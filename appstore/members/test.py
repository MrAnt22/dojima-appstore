from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post, Profile, Review, Comment, Category

class AppStoreTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123', is_staff=True)  # is_staff додано
        self.category = Category.objects.create(name='Utilities')

    def test_registration_view(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)

    def test_create_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('create_post'), {
            'title': 'My App',
            'description': 'Test description',
            'type': 'app',
            'categories': [self.category.id]
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='My App').exists())

    def test_view_post(self):
        post = Post.objects.create(
            user=self.user,
            title='Post Title',
            description='Content',
            type='post'
        )
        response = self.client.get(reverse('post', kwargs={
            'post_type': 'post',
            'post_id': post.id
        }))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Post Title')

    def test_add_comment(self):
        self.client.login(username='testuser', password='testpass123')
        post = Post.objects.create(
            user=self.user,
            title='News',
            description='Just text',
            type='post'
        )
        response = self.client.post(reverse('post', kwargs={
            'post_type': 'post',
            'post_id': post.id
        }), {
            'content': 'Nice one!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(post=post, content='Nice one!').exists())

    def test_add_review(self):
        self.client.login(username='testuser', password='testpass123')
        post = Post.objects.create(
            user=self.user,
            title='App',
            description='App desc',
            type='app'
        )
        response = self.client.post(reverse('post', kwargs={
            'post_type': 'app',
            'post_id': post.id
        }), {
            'rating': 5,
            'content': 'Excellent app!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(post=post, rating=5).exists())

    def test_like_toggle(self):
        self.client.login(username='testuser', password='testpass123')
        post = Post.objects.create(
            user=self.user,
            title='Likeable',
            description='Like me',
            type='post'
        )
        like_url = reverse('toggle_like', kwargs={'post_id': post.id})

        # First like
        self.client.get(like_url)
        self.assertTrue(post.likes.filter(id=self.user.id).exists())

        # Unlike
        self.client.get(like_url)
        self.assertFalse(post.likes.filter(id=self.user.id).exists())
