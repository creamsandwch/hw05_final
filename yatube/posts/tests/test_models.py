from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        model_str = {
            PostModelTest.post: 'Тестовый пост',
            PostModelTest.group: 'Тестовая группа',
        }
        for object, __str__ in model_str.items():
            with self.subTest(object=object):
                self.assertEqual(str(object), __str__)

    def test_post_model_have_correct_verbose_names(self):
        """Проверяем, что у полей моделей корректно заданы verbose-имена"""
        field_verbose_names = {
            'text': 'Текст поста',
            'created': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verbose_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).verbose_name,
                    expected_value.lower()
                )

    def test_post_model_have_correct_help_text(self):
        """Проверяем, что у полей модели корректно заданы help_text"""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).help_text,
                    expected_value
                )
