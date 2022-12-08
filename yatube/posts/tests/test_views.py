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
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html'
            }
        """ Проверяем, что при обращении к name вызывается
            соответствующий HTML-шаблон"""
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, 'Text_post')
        self.assertEqual(post_group_0, 'Aga')

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expected)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        group_title_test_0 = first_object.group.title
        self.assertEqual(post_text_0, 'Text_post')
        self.assertEqual(group_title_test_0, 'Aga')


"""class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author5')
        cls.group = Group.objects.create(
            title='Test group',
            slug='Test_slug',
            description='Description'
        )
        for i in range(1, 14):
            cls.post = Post.objects.create(
                text='Text_post',
                author=cls.author,
                group=cls.group
            )
        cls.author = Client()
        cls.author.force_login(cls.author)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Author6')
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
                ААААААААААААААААААААААААААААААААААААААААААААААААААА
                типо черта от какого то говна, главное не забыт ьудалить

    def test_post_list_page_show_correct_context(self):
        Шаблон group_post сформирован с правильным контекстом.
        response = self.authorized_client.get(reverse('posts:group_list'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['object_list'][0]
        task_title_0 = first_object.title
        task_description_0 = first_object.text
        task_slug_0 = first_object.slug
        self.assertEqual(task_title_0, 'Заголовок')
        self.assertEqual(task_description_0, 'Текст')
        self.assertEqual(task_slug_0, 'test-slug')"""






