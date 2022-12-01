from django.test import TestCase, Client
from http import HTTPStatus


class AboutURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_url_exists_at_desired_location(self):
        """Страницы /about/author/ и /about/tech/
        доступны любому пользователю."""
        urls = [
            '/about/author/',
            '/about/tech/',
        ]
        for url in urls:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
