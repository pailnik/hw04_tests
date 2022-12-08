from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='rats',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовая запись Формы',
            author=cls.user,
            group=cls.group
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тест-test Post-Пост',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(('posts:profile'),
                    kwargs={'username': 'auth'})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тест-test Post-Пост',
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тест-test Post-Пост',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        """Валидная форма редактирует запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тест Пост',
            'group': self.group.id,
        }
        post = Post.objects.get(text='Тест-test Post-Пост')
        post_id = post.id
        self.authorized_client.post(
            reverse(('posts:post_edit'),
                    args=(post.id,)),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text='Тест Пост',
            ).exists()
        )
        edited_post = Post.objects.get(text='Тест Пост')
        self.assertEqual(edited_post.id, post_id)