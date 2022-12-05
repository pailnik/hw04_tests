from django.contrib.auth import get_user_model

from ..forms import PostForm
from ..models import Post, Group
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в базе данных для проверки сушествующего slug
        cls.user = User.objects.create(username='Wanderer')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            id=5,
        )
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()

    def test_create_task(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Task
        posts_count = Post.objects.count()
        form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('posts:profile'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:profile'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                slug='testovyij-zagolovok',
                text='Тестовый текст',
            ).exists()
        )
