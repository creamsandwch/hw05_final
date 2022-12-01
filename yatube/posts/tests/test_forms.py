import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings

from posts.models import Post, Group, User, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """Форма для создания и редактирования поста."""
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.author)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
        )
        cls.author = User.objects.create(username='TestUser')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_image = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.author,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_postform_creates_post(self):
        """Валидная форма PostForm создаёт запись в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': PostFormTests.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostFormTests.author.username}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=PostFormTests.group,
                author=PostFormTests.author
            ).exists(),
            'Создаваемый пост не обнаружен в БД.'
        )

    def test_postform_edits_post(self):
        """Валидная форма PostForm редактирует запись в БД."""
        form_data = {
            'text': 'Отредактировано',
            'group': PostFormTests.group.pk,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post.id},
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostFormTests.post.id}
            ),
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=PostFormTests.group,
                author=PostFormTests.author
            ).exists(),
            ('Отредактированный пост не был записан в БД.')
        )

    def test_thumbnail_sent_in_post_form(self):
        """Проверяем, создается ли пост, если в PostForm отправить
        картинку."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'author': PostFormTests.author.pk,
            'group': PostFormTests.group.pk,
            'image': PostFormTests.uploaded_image,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertEqual(posts_count + 1, Post.objects.count())
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=PostFormTests.group,
                author=PostFormTests.author,
                image='posts/small.gif',
            )
        )

    def test_commentform_creates_comment(self):
        """Валидная форма CommentForm создает запись в БД."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария.',
            'post': PostFormTests.post.pk,
            'author': PostFormTests.author.pk,
        }
        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostFormTests.post.id}
            ),
            data=form_data
        )
        self.assertEqual(
            comments_count + 1,
            Comment.objects.count(),
            'Комментарий не был записан в БД.')
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                post=PostFormTests.post,
                author=PostFormTests.author,
            ),
            'Данные комментария были переданы формой некорректно.'
        )

    def test_unauthorized_user_cant_comment_on_post(self):
        """Проверяем, что неавторизованный пользователь не может
        комментировать посты."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария.',
            'post': PostFormTests.post.pk,
            'author': PostFormTests.author.pk,
        }
        self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostFormTests.post.id}
            ),
            data=form_data,
        )
        self.assertEqual(
            comments_count,
            Comment.objects.count(),
            'Комментарий был записан в БД неавторизованным пользователем.'
        )
