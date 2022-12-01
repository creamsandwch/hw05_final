from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User


class UserFormTest(TestCase):
    @classmethod
    def setUp(self):
        self.guest_client = Client()

    def test_creationform_creates_new_user(self):
        """Валидная форма CreationForm создаёт новую запись в БД."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'TestUser',
            'email': 'testuser@ya.ru',
            'password1': '1233passWORD',
            'password2': '1233passWORD',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:index')
        )
        self.assertEqual(
            User.objects.count(),
            users_count + 1,
            'Количество записей в БД не изменилось.'
        )
        self.assertTrue(
            User.objects.filter(
                first_name='Test',
                last_name='User',
                username='TestUser',
                email='testuser@ya.ru'
            ).exists(),
            'Создаваемый пользователь не обнаружен в БД.'
        )
