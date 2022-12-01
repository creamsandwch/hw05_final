# posts/tests/test_urls.py
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import User, Post, Group


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticURLTests.author)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.author,
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
        )

    def test_homepage(self):
        """Проверяем доступность главной страницы (smoke test)."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_non_existent_page(self):
        """Проверяем недоступность несуществующей страницы."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_exist_at_desired_location(self):
        """Проверяем доступность всех остальных url-адресов."""
        urls = [
            '/',
            f'/group/{StaticURLTests.group.slug}/',
            f'/profile/{StaticURLTests.author.username}/',
            f'/posts/{StaticURLTests.post.id}/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_templates_used(self):
        """Проверяем, верный ли шаблон используется при обращении по
        соответствующему адресу."""
        urls_templates = [
            ('/', 'posts/index.html'),
            (f'/group/{StaticURLTests.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{StaticURLTests.author.username}/',
             'posts/profile.html'),
            (f'/posts/{StaticURLTests.post.id}/', 'posts/post_detail.html'),
            (f'/posts/{StaticURLTests.post.id}/edit/',
             'posts/create_post.html'),
            ('/create/', 'posts/create_post.html'),
        ]
        for url_expected_template in urls_templates:
            with self.subTest(url=url_expected_template[0]):
                response = self.authorized_client.get(url_expected_template[0])
                self.assertTemplateUsed(response, url_expected_template[1])
