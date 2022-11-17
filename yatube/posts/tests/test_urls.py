import shutil
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer
from posts.models import Group

User = get_user_model()


@override_settings(MEDIA_ROOT=settings.TEMP_MEDIA_ROOT)
class PostURLTests(TestCase):
    """Проверка url-ов.

    Проверяем корректность http-статусов.
    Проверяем корректность отображения шаблонов.
    Проверяем корректность редиректов.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Создаём данные для тестов и логиним."""
        super().setUpClass()

        cls.user = User.objects.create_user(username='test_user')
        cls.user_author = User.objects.create_user(username='test_user_author')
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(
            'posts.Post',
            author=cls.user_author,
        )

        cls.anon = Client()
        cls.client_auth = Client()
        cls.client_author = Client()
        cls.client_auth.force_login(cls.user)
        cls.client_author.force_login(cls.user_author)

        cls.urls = {
            'ad_comment': reverse('posts:add_comment', args=(cls.post.id,)),
            'create': reverse('posts:post_create'),
            'detail': reverse('posts:post_detail', args=(cls.post.id,)),
            'edit': reverse('posts:post_edit', args=(cls.post.id,)),
            'follow': reverse('posts:follow_index'),
            'group': reverse('posts:group_list', args=(cls.group.slug,)),
            'index': reverse('posts:index'),
            'profile': reverse('posts:profile', args=(cls.user.username,)),
            'profile_follow': reverse(
                'posts:profile_follow',
                args=(cls.user.username,),
            ),
            'profile_unfollow': reverse(
                'posts:profile_unfollow',
                args=(cls.user.username,),
            ),
            'missing': '/unexisting_page/',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def test_http_statuses(self):
        """Проверяем http-cтатусы url-в разными пользователями."""
        httpstatuses = (
            (self.urls.get('ad_comment'), HTTPStatus.FOUND, self.client_auth),
            (self.urls.get('create'), HTTPStatus.OK, self.client_auth),
            (self.urls.get('create'), HTTPStatus.FOUND, self.anon),
            (self.urls.get('detail'), HTTPStatus.OK, self.client_auth),
            (self.urls.get('edit'), HTTPStatus.OK, self.client_author),
            (self.urls.get('edit'), HTTPStatus.FOUND, self.client_auth),
            (self.urls.get('follow'), HTTPStatus.OK, self.client_auth),
            (self.urls.get('group'), HTTPStatus.OK, self.anon),
            (self.urls.get('index'), HTTPStatus.OK, self.anon),
            (self.urls.get('profile'), HTTPStatus.OK, self.client_auth),
            (
                self.urls.get('profile_follow'),
                HTTPStatus.FOUND,
                self.client_auth,
            ),
            (
                self.urls.get('profile_unfollow'),
                HTTPStatus.FOUND,
                self.client_auth,
            ),
            (
                self.urls.get('missing'),
                HTTPStatus.NOT_FOUND,
                self.client_auth,
            ),
        )

        for url, response_code, auth_status in httpstatuses:
            with self.subTest(url=url):
                self.assertEqual(
                    auth_status.get(url).status_code,
                    response_code,
                )

    def test_templates(self):
        """Проверяем шаблоны url-в разными пользователями."""
        templates = (
            (
                self.urls.get('create'),
                'posts/create_post.html',
                self.client_auth,
            ),
            (
                self.urls.get('detail'),
                'posts/post_detail.html',
                self.anon,
            ),
            (
                self.urls.get('edit'),
                'posts/create_post.html',
                self.client_author,
            ),
            (
                self.urls.get('follow'),
                'posts/follow.html',
                self.client_auth,
            ),
            (
                self.urls.get('group'),
                'posts/group_list.html',
                self.anon,
            ),
            (
                self.urls.get('index'),
                'posts/index.html',
                self.anon,
            ),
            (
                self.urls.get('profile'),
                'posts/profile.html',
                self.client_auth,
            ),
        )
        for url, template, auth_status in templates:
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    auth_status.get(url),
                    template,
                    f'Ошибка: {url} ожидал шаблон {template}',
                )

    def test_redirects(self):
        """Проверяем редиреркты url-в разными пользователями."""
        redirects = (
            (
                self.urls.get('create'),
                redirect_to_login(self.urls.get('create')).url,
                self.anon,
            ),
            (
                self.urls.get('edit'),
                redirect_to_login(self.urls.get('edit')).url,
                self.anon,
            ),
            (
                self.urls.get('edit'),
                self.urls.get('detail'),
                self.client_auth,
            ),
        )
        for url, redirect, authlevel in redirects:
            with self.subTest(url=url):
                self.assertRedirects(
                    authlevel.get(url),
                    redirect,
                )
