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
        cls.user = User.objects.create(username='VagA')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Текст',
            group=cls.group,
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': 'slug'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.post.author}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def post_attr(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)

    def test_three_templates_correct_context(self):
        """Шаблоны сформированы с правильным контекстом"""
        urls = {
            'posts:index': None,
            'posts:group_list': {'slug': self.group.slug},
            'posts:profile': {'username': self.user.username},
        }
        for name_url, data in urls.items():
            with self.subTest(name_url=name_url):
                response = self.authorized_client.get(reverse(
                    name_url, kwargs=data))
                self.post_attr(response.context.get('page_obj').
                               object_list[0])

    def test_post_create_page_correct_context(self):
        """Шаблон POST_CREATE сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_edit_page_correct_context(self):
        """Шаблон POST_CREATE_EDIT сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_detail_page_correct_context(self):
        """Шаблон post_detail_ сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.post_attr(response.context.get('post'))

    def test_group_list_context(self):
        """Шаблон group_list"""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        expected = list(Post.objects.filter(group_id=self.group.id)[:10])
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_index_context(self):
        response = self.guest_client.get(reverse('posts:index'))
        expected = list(Post.objects.all()[:10])
        self.assertEqual(list(response.context['page_obj']), expected)

    def check_group(self):
        form_fields = {
            reverse('posts:index'): Post.objects.get(group=self.post.group),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): Post.objects.get(group=self.post.group),
            reverse(
                'posts:profile', kwargs={'username': self.post.author}
            ): Post.objects.get(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertIn(expected, form_field)

    def test_check_group_not_in_mistake_group_list_page(self):
        """Проверяем чтобы созданный
        Пост с группой не попап в чужую группу."""
        form_fields = {
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): Post.objects.exclude(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertNotIn(expected, form_field)


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

        for i in range(1, 13):
            cls.post = Post.objects.create(
                text='Test_post',
                author=cls.author,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Wanderer')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        Paginator_obj = {
            reverse('posts:index'): 10,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 10,
            reverse('posts:profile',
                    kwargs={'username': self.author}): 10,
        }
        for page, number in Paginator_obj.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(len(response.context['page_obj']),
                                 number)

    def test_second_page_contains_three_records(self):
        Paginator_obj = {
            reverse('posts:index'): 3,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 3,
            reverse('posts:profile',
                    kwargs={'username': self.author}): 3,
        }
        for page, number in Paginator_obj.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 number)
