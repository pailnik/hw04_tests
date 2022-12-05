from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        cls.author = User.objects.create(username='VagA')
        cls.group = Group.objects.create(
            title='Aga',
            slug='slug_slug',
            description='description',
        )
        cls.post = Post.objects.create(
            text='Text_post',
            group=cls.group,
            author=cls.author,
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='Wanderer')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list'),
            'posts/profile.html': reverse('posts:profile'),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'slug': 'test-slug'})
            ),
            'posts/create_post.html': reverse('posts:post_edit'),
            'posts/create_post.html': reverse('posts:create_post'),

        }
        # Проверяем, что при обращении к name вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_detail_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_detail'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'group': forms.fields.CharField,
            'text': forms.fields.CharField,
            # 'slug': forms.fields.SlugField,
            # 'image': forms.fields.ImageField,
        }

        # Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон task_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail', kwargs={'slug': 'test-slug'})))
        self.assertEqual(response.context.get('task').title, 'Заголовок')
        self.assertEqual(response.context.get('task').text, 'Текст')
        self.assertEqual(response.context.get('task').slug, 'test-slug')

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.author.
                    get(reverse('posts:post_detail',
                                kwargs={'post_id': self.post.id, 'username':
                                    self.author})))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        cls.author = User.objects.create(username='VagA')
        cls.group = Group.objects.create(
            title='Aga',
            slug='slug_slug',
            description='description',
        )
        cls.post = Post.objects.create(
            text='Text_post',
            group=cls.group,
            author=cls.author,
        )

        for i in range(1, 12):
            cls.post = Post.objects.create(
                text='Test_post',
                author=cls.author,
                group=cls.group
            )

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='Wanderer')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        Paginator_obj = {
            reverse('posts:index'): 10,
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}): 10,
            reverse('posts:profile', kwargs={'username': self.author}): 10,
        }
        for page, number in Paginator_obj.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(len(response.context['page_obj']), number)

    def test_second_page_contains_three_records(self):
        Paginator_obj = {
            reverse('posts:index'): 3,
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}): 3,
            reverse('posts:profile', kwargs={'username': self.author}): 3,
        }
        for page, number in Paginator_obj.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page + '?page=2')
                self.assertEqual(len(response.context['page_obj']), number)

# Какая то лютая хуйня как это делать не ебу
# ошибки 6 из 6 в рот их ебать
