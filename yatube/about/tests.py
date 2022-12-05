from http import HTTPStatus

from django.test import TestCase


class AboutURLTest(TestCase):
    def test_url_exists_at_desired_location(self):
        """Страницы /about/author/ и /about/tech/
        доступны любому пользователю."""
        urls = [
            '/about/author/',
            '/about/tech/',
        ]
        for url in urls:
            with self.subTest(f'url "{url}" не найден.'):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
