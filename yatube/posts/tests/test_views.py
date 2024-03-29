import shutil

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer
from posts.models import Follow, Group, Post
from posts.tests.common import image

User = get_user_model()


@override_settings(MEDIA_ROOT=settings.TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    """
    Тестирование работы view-функций namespace posts.

    NUMBER_OF_CONTEXT: индекс извлекаемого контекстного значения.
    """

    NUMBER_OF_CONTEXT: int = 0

    @classmethod
    def setUpClass(cls):
        """Создаём данные для тестов и логиним."""
        super().setUpClass()

        cls.user = User.objects.create_user(username='test_author')
        cls.group = mixer.blend(Group)
        cls.post = Post.objects.create(
            text='test_text',
            group=cls.group,
            author=cls.user,
            image=image(),
        )

        cls.anon = Client()
        cls.client_user = Client()
        cls.client_user.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def test_index_page_show_correct_context(self):
        """Проверяем что шаблон index сформирован с правильным контекстом."""
        response = self.client_user.get(reverse('posts:index'))
        post = response.context['post']
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(str(post.group), self.group.title)
        self.assertEqual(post.image, self.post.image)

    def test_group_list_page_show_correct_context(self):
        """Проверяем что шаблон group_list сформ. с правильным контекстом."""
        response = self.client_user.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        post = response.context['page_obj'][0]
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(str(post.group), self.group.title)
        self.assertEqual(post.image, self.post.image)

    def test_profile_show_correct_context(self):
        """Проверяем что шаблон profile сформирован с правильным контекстом."""
        response = self.client_user.get(
            reverse('posts:profile', args=(self.user.username,)),
        )
        post = response.context['page_obj'][
            self.NUMBER_OF_CONTEXT
        ]
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(str(post.group), self.group.title)
        self.assertEqual(post.image, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Проверяем что шаблон post_detail сформ. с правильным контекстом."""
        response = self.client_user.get(
            reverse('posts:post_detail', args=(self.post.pk,)))
        self.assertEqual(response.context.get('post').pk, self.post.pk)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get(
            'post').author, self.post.author)
        self.assertEqual(response.context.get(
            'post').group, self.post.group)
        self.assertEqual(response.context.get('post').image, self.post.image)

    def test_create_post_show_correct_context(self):
        """Проверяем что шаблон create_post сформ. с правильным контекстом."""
        response = self.client_user.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Проверяем что шаблон post_edit сформ. с правильным контекстом."""
        response = self.client_user.get(
            reverse('posts:post_edit', args=(self.post.pk,)))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_created_post_show_correct_context(self):
        """Проверка что пост отображается с правильным контекстом."""
        test_user = User.objects.create_user(
            username='test_author_created_post',
        )
        test_group = mixer.blend(Group)
        test_post = Post.objects.create(
            text='test_text_created_post',
            author=test_user,
            group=test_group,
        )
        list_page_name = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                args=(test_group.slug,),
            ),
            reverse(
                'posts:profile',
                args=(test_user.username,),
            ),
        )
        for name_page in list_page_name:
            with self.subTest(name_page=name_page):
                response = self.client_user.get(name_page)
                post = response.context['page_obj'][
                    self.NUMBER_OF_CONTEXT
                ]
                response = self.client_user.get(
                    reverse(
                        'posts:group_list',
                        args=(self.group.slug,),
                    ),
                )
                group_test_slug = response.context['page_obj'][
                    self.NUMBER_OF_CONTEXT
                ]
                self.assertEqual(post, test_post)
                self.assertNotEqual(post, group_test_slug)

    def test_cache_index_page(self):
        """Проверка работы кеша."""
        post = Post.objects.create(
            text='пост под кеш',
            author=self.user)
        content_add = self.client_user.get(
            reverse('posts:index')).content
        post.delete()
        content_delete = self.client_user.get(
            reverse('posts:index')).content
        self.assertEqual(content_add, content_delete)
        cache.clear()
        content_cache_clear = self.client_user.get(
            reverse('posts:index')).content
        self.assertNotEqual(content_add, content_cache_clear)


class PaginatorViewsTest(TestCase):
    """Тестирование паджинации.

    Здесь создаются фикстуры: клиент и
    15 тестовых записей NUMBER_OF_POSTS.

    NUMBER_OF_POSTS_SECOND_PAGE: количество выводимых
    постов для второй страницы.
    """

    NUMBER_OF_POSTS: int = 15
    NUMBER_OF_POSTS_SECOND_PAGE: int = 5

    @classmethod
    def setUpClass(cls):
        """Создаём данные для тестов и логиним."""
        super().setUpClass()

        cls.user = User.objects.create_user(username='test_author')
        cls.group = mixer.blend(Group)

        for cls.post_number in range(cls.NUMBER_OF_POSTS):
            cls.post_fill = Post.objects.create(
                text=f'Пост {cls.post_number} в тесте!',
                group=cls.group,
                author=cls.user,
            )
        cls.paginated = (
            ('posts:index', 'posts/index.html', None),
            ('posts:profile', 'posts/profile.html', (cls.user.username,)),
            ('posts:group_list', 'posts/group_list.html', (cls.group.slug,)),
        )

        cls.anon = Client()
        cls.client_auth = Client()
        cls.client_auth.force_login(cls.user)

    def setUP(self):
        cache.clear()

    def test_first_and_second_page_paginate_correct(self):
        """Проверка вывода количества постов на первую и вторую страницы."""
        for pages in self.paginated:
            name, template, arg = pages
            reverse_name = reverse(name, args=arg)
            with self.subTest(reverse_name=reverse_name):
                response = self.client_auth.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.LIMIT_POSTS,
                    f'Ошибка: Пагинатор не выводит на первую страницу'
                    f'{template} 10 постов',
                )
                response = self.client_auth.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.NUMBER_OF_POSTS_SECOND_PAGE,
                    f'Ошибка: Пагинатор не выводит на вторую страницу'
                    f'{template} 5 постов',
                )


class FollowViewsTest(TestCase):
    """Тестирование view-функций отвечающих за работу подписки."""

    @classmethod
    def setUpClass(cls):
        """Создаём данные для тестов и логиним."""
        super().setUpClass()

        cls.post_author = User.objects.create_user(
            username='post_author',
        )
        cls.post_follower = User.objects.create_user(
            username='post_follower',
        )
        cls.post = Post.objects.create(
            text='подпишись на меня',
            author=cls.post_author,
        )

        cls.client_author = Client()
        cls.follower_client = Client()
        cls.client_author.force_login(cls.post_follower)
        cls.follower_client.force_login(cls.post_author)

    def setUp(self):
        cache.clear()

    def test_follow_on_user(self):
        """Проверка подписки на пользователя."""
        self.follower_client.post(
            reverse(
                'posts:profile_follow',
                args=(self.post_follower,),
            ),
        )
        follow = Follow.objects.get()
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(follow.author_id, self.post_follower.id)
        self.assertEqual(follow.user_id, self.post_author.id)

    def test_unfollow_on_user(self):
        """Проверка отписки от пользователя."""
        Follow.objects.create(
            user=self.post_author,
            author=self.post_follower,
        )
        self.follower_client.post(
            reverse(
                'posts:profile_unfollow',
                args=(self.post_follower,),
            ),
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_follow_on_authors(self):
        """Проверка записей у тех кто подписан."""
        post = Post.objects.create(
            author=self.post_author,
            text='подпишись на меня')
        Follow.objects.create(
            user=self.post_follower,
            author=self.post_author)
        response = self.client_author.get(
            reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'].object_list)

    def test_notfollow_on_authors(self):
        """Проверка записей у тех кто не подписан."""
        post = Post.objects.create(
            author=self.post_author,
            text='подпишись на меня')
        response = self.client_author.get(
            reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'].object_list)
