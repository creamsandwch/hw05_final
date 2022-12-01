from http import HTTPStatus

from django.test import Client, TestCase


class CoreViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_custom_templates_for_404(self):
        """Проверяем, используется ли кастомный шаблон для страницы
        с ошибкой 404."""
        response = self.guest_client.get('/unexistent-page/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            '''Страница /unexistent-page/ не выдает ошибку 404'''
        )
        self.assertTemplateUsed(
            response,
            'core/404.html',
            msg_prefix='Используется некорретный шаблон'
        )
