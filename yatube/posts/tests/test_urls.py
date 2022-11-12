from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from mixer.backend.django import mixer

from posts.models import Group, Post

User = get_user_model()


# Аня , твой комментарий увидел. Могу на каникулах повозиться.
class PostURLTests(TestCase):
    """Устанавливаем данные для тестирования posts/urls."""

    @classmethod
    def setUpClass(cls):
        """Создаём тестовую записи в БД.

        Сохраняем созданную запись в качестве переменной класса.
        """
        super().setUpClass()

        cls.anon = Client()
        cls.client = Client()

        cls.user = User.objects.create_user(username='test_author')

        cls.group = mixer.blend(Group)
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_text',
            group=cls.group,
        )
        cls.client.force_login(cls.user)
        cls.group_list_url = f'/group/{cls.group.slug}/'
        cls.post_edit_url = f'/posts/{cls.post.pk}/edit/'
        cls.post_url = f'/posts/{cls.post.pk}/'
        cls.profile_url = f'/profile/{cls.user.username}/'
        cls.public_urls = (
            ('', 'posts/index.html'),
            (cls.group_list_url, 'posts/group_list.html'),
            (cls.post_url, 'posts/post_detail.html'),
            (cls.profile_url, 'posts/profile.html'),
        )
        cls.private_urls = (
            ('/create/', 'posts/create_post.html'),
            (cls.post_edit_url, 'posts/create_post.html'),
        )

    def setUp(self):
        cache.clear()

    def test_anon_public_pages_url_exists(self):
        """Проверка что все общие страницы доступны.

        Для неавторизованного пользователя.
        """
        for pages in self.public_urls:
            url, name = pages
            with self.subTest(url=url):
                response = self.anon.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK.value,
                    f'Ошибка: {name} для {self.anon} не доступен',
                )

    def test_anon_private_pages_url_exists(self):
        """Проверка что все приватные страницы недоступны.

        Для неавторизованного пользователя.
        """
        for pages in self.private_urls:
            url, name = pages
            with self.subTest(url=url):
                response = self.anon.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.FOUND.value,
                    f'Ошибка: {url} доступен для неавторизованного'
                    f'пользователя на {name}',
                )

    def test_auth_private_pages_url_exists(self):
        """Проверка что все прив. страницы доступны для авт. пол-ля."""
        for pages in self.private_urls:
            url, name = pages
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK.value,
                    f'Ошибка: {name} для {self.client} не доступен',
                )

    def test_private_urls_uses_correct_templates(self):
        """Проверка url-адресов требующие авторизации.

        Используют соответствующий шаблон.
        """
        for pages in self.private_urls:
            url, name = pages
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(
                    response,
                    name,
                    f'Ошибка: {url} ожидал шаблон {name}',
                )

    def test_public_urls_uses_correct_templates(self):
        """Проверка url-адресов используют соответствующий шаблон."""
        for pages in self.public_urls:
            url, name = pages
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(
                    response,
                    name,
                    f'Ошибка: {url} ожидал шаблон {name}',
                )
