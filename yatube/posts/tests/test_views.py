import tempfile
import shutil
from random import randint

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache
from django import forms

from ..models import User, Post, Group, Comment
from django.conf import settings


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
)
class PostViewsTest(TestCase):
    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsTest.author)
        self.guest_client = Client()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestUser')
        cls.group_1 = Group.objects.create(
            title='Первая тестовая группа',
            slug='test-slug-1',
        )
        cls.group_2 = Group.objects.create(
            title='Вторая тестовая группа',
            slug='test-slug-2'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.test_post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group_1,
            author=cls.author,
            image=cls.uploaded
        )
        cls.test_comment = Comment.objects.create(
            text='Текст комментария',
            post=cls.test_post,
            author=cls.author,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def fill_post_fields(self, slug_num):
        """Возвращает словарь, где ключами являются атрибуты поста,
        а значениями - тестовые значения из setUpClass. Параметр slug_num
        влияет на то, какая группа будет выбрана в словаре из двух тестовых."""
        post_fields = {}
        post_fields['text'] = PostViewsTest.test_post.text
        if slug_num == 1:
            post_fields['group'] = PostViewsTest.group_1
        else:
            post_fields['group'] = PostViewsTest.group_2
        post_fields['author'] = PostViewsTest.author
        return post_fields

    def test_sent_comment_shows_in_post_detail_context(self):
        """Проверяем, что в контекст страницы с детальными данными
        о посте передается комментарий к посту."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTest.test_post.id}
            )
        )
        self.assertContains(
            response,
            PostViewsTest.test_comment,
            msg_prefix='Комментарий к посту не отображен на странице.'
        )

    def test_views_use_correct_templates(self):
        """Проверяем, что view-функции приложения posts
        используют правильные шаблоны."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTest.group_1.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTest.test_post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTest.test_post.author.username}
            ): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewsTest.test_post.id}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_view_show_correct_context(self):
        """Проверяем, что post_create и post_view передает правильный
        context (форма) шаблону при get-запросе."""
        urls = [
            reverse('posts:post_create'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewsTest.test_post.id}
            ),
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for url in urls:
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    response = self.authorized_client.get(url)
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_index_shows_correct_context(self):
        """Проверяем, что index view передает правильный
        context шаблону"""
        response = self.guest_client.get(reverse('posts:index'))
        object_list = response.context['page_obj'].object_list
        post_fields = self.fill_post_fields(slug_num=1)
        self.assertIn(
            PostViewsTest.test_post,
            object_list,
            'Пост не передан в контексте'
        )
        for value, expected in post_fields.items():
            with self.subTest(value=value):
                self.assertEqual(
                    getattr(PostViewsTest.test_post, value),
                    expected,
                    'Данные поста неверно переданы в шаблон'
                )

    def test_group_list_view_shows_correct_context(self):
        """Проверяем, что group_list view передает правильный
        context шаблону"""
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTest.group_2.slug}
            )
        )
        self.assertContains(
            response,
            PostViewsTest.group_2,
            msg_prefix='В контекст не передана группа, или передана неверная:'
        )
        post_attr = self.fill_post_fields(slug_num=1)
        for value, expected in post_attr.items():
            with self.subTest(value=value):
                self.assertEqual(
                    getattr(PostViewsTest.test_post, value),
                    expected,
                    'Данные поста неверно переданы в шаблон'
                )

    def test_group_list_view_shows_correct_group(self):
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTest.group_2.slug}
            )
        )
        object_list = response.context['page_obj'].object_list
        self.assertNotIn(
            PostViewsTest.test_post,
            object_list,
            'Ошибка: пост передан в контекст страницы чужой группы'
        )

    def test_post_profile_view_shows_correct_context(self):
        """Проверяем, что profile_view передает правильный
        контекст"""
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTest.author.username}
            )
        )
        self.assertContains(
            response,
            PostViewsTest.test_post,
            msg_prefix=(
                'В контекст не передан тестовый пост,'
            )
        )
        post_attrs = self.fill_post_fields(slug_num=1)
        for value, expected in post_attrs.items():
            with self.subTest(value=value):
                self.assertEqual(
                    getattr(PostViewsTest.test_post, value),
                    expected,
                    'Данные поста неверно переданы в шаблон'
                )

    def test_post_profile_view_shows_post(self):
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTest.author.username}
            )
        )
        object_list = response.context['page_obj'].object_list
        self.assertIn(
            PostViewsTest.test_post,
            object_list,
            ('Ошибка: пост не был передан'
             ' в контексте страницы профиля автора поста')
        )

    def test_post_detail_view_shows_correct_context(self):
        """Проверяем, что detail_view правильно передает context."""
        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTest.test_post.id}
            )
        )
        post_attrs = self.fill_post_fields(slug_num=1)
        post = response.context['post']
        for value, expected in post_attrs.items():
            with self.subTest(value=value):
                self.assertEqual(getattr(post, value), expected)

    def test_if_group_is_set_post_is_on_pages(self):
        """Проверяем, что если при создании поста указать
        группу, он появится на главной, странице группы
        и профиле пользователя"""
        urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTest.group_1.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTest.author.username}
            ),
        ]
        for url in urls:
            response = self.guest_client.get(url)
            object_list = response.context['page_obj'].object_list
            self.assertIn(
                PostViewsTest.test_post,
                object_list,
                ('Пост с заданной группой не отправлен на'
                 f'страницу по адресу {response}')
            )

    def test_views_show_thumbnail_in_pages_context(self):
        """Проверяем, что на всех страницах, где отображается пост
        с картинкой, он отображается корректно."""
        urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTest.group_1.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTest.author.username}
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTest.test_post.id}
            )
        ]
        for url in urls:
            response = self.authorized_client.get(url)
            if response.context.get('page_obj'):
                self.assertEqual(
                    response.context.get('page_obj')[0],
                    PostViewsTest.test_post,
                    ('Пост с прикрепленной картинкой не найден '
                     f'по адресу {url}')
                )
            else:
                self.assertEqual(
                    response.context.get('post'),
                    PostViewsTest.test_post,
                    ('Пост с прикрепленной картинкой не найден '
                     f'по адресу {url}')
                )

    def test_index_page_is_cached(self):
        """Проверяем работу кэша главной страницы."""
        data_dict = {
            'text': 'Пост для проверки кеширования',
            'author': PostViewsTest.author,
            'group': PostViewsTest.group_1
        }
        cache_test_post = Post.objects.create(**data_dict)
        response = self.guest_client.get(reverse('posts:index'))
        Post.objects.filter(**data_dict).delete()
        self.assertContains(
            response,
            cache_test_post.text,
            msg_prefix='Пост не остался в кэше страницы'
        )
        cache.clear()
        response = self.guest_client.get(reverse('posts:index'))
        self.assertNotContains(
            response,
            cache_test_post.text,
            msg_prefix='Пост не был удалён из кэша страницы'
        )


class TestPaginator(TestCase):
    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(TestPaginator.author)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Первая тестовая группа',
            slug='test-slug-1',
        )
        cls.post_list = []
        cls.first_page_obj_count = settings.POSTS_VIEWED
        cls.second_page_obj_count = randint(1, settings.POSTS_VIEWED)
        posts_created_count = (
            cls.first_page_obj_count
            + cls.second_page_obj_count
        )
        for i in range(posts_created_count):
            cls.post_list.append(
                Post(
                    text=f'Текст тестового поста #{i}',
                    author=cls.author,
                    group=cls.group,
                )
            )
        Post.objects.bulk_create(
            cls.post_list
        )

    def test_pagination_first_page(self):
        """Проверяем корректность работы паджинатора
        (кол-во постов на первой странице)"""
        reversed_urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': TestPaginator.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': TestPaginator.author.username}
            )
        ]
        for url in reversed_urls:
            response = self.authorized_client.get(url)
            self.assertEqual(
                TestPaginator.first_page_obj_count,
                len(response.context['page_obj']),
                ('Количество постов не равно'
                 f' {TestPaginator.first_page_obj_count}'
                 f'на первой странице {url}')
            )

    def pagination_second_page(self):
        """Проверяем корректность работы паджинатора (кол-во)
        постов на второй странице."""
        reversed_urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': TestPaginator.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': TestPaginator.author.username}
            )
        ]
        for url in reversed_urls:
            response = self.authorized_client.get(url + '?page=2')
            self.assertEqual(
                TestPaginator.second_page_obj_count,
                len(response.context['page_obj']),
                (f'Количество постов не равно'
                 f' {TestPaginator.second_page_obj_count}'
                 f' на второй странице {url}')
            )
