import shutil

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = 'media/posts'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    """
    Устанавливаем данные для тестирования posts/forms.

    NUMBER_OF_CONTEXT: индекс извлекаемого контекстного значения.
    """

    NUMBER_OF_CONTEXT: int = 0

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.anon = Client()
        cls.client = Client()

        cls.user = User.objects.create_user(username='test_author')

        cls.group = mixer.blend(Group)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )
        cls.post = Post.objects.create(
            text='test_text',
            group=cls.group,
            author=cls.user,
            image=cls.uploaded,
        )

    def setUp(self):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('posts:index'))
        post = response.context['post']
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(str(post.group), self.group.title)
        self.assertEqual(post.image, self.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        post = response.context['page_obj'][0]
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(str(post.group), self.group.title)
        self.assertEqual(post.image, self.post.image)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        self.client.force_login(self.user)
        response = self.client.get(
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
        """Шаблон post_detail сформирован с правильным контекстом."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('posts:post_detail', args=(self.post.pk,)))
        self.assertEqual(response.context.get('post').pk, self.post.pk)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get(
            'post').author, self.post.author)
        self.assertEqual(response.context.get(
            'post').group, self.post.group)
        self.assertEqual(response.context.get('post').image, self.post.image)

    def test_create_post_show_correct_context(self):
        """Проверка шаблона create_post для создания поста.

        Сформирован с правильным контекстом.
        """
        self.client.force_login(self.user)
        response = self.client.get(
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
        """Шаблон post_edit сформирован с правильным контекстом."""
        self.client.force_login(self.user)
        response = self.client.get(
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
        """Проверка отображения поста с правильным контекстом."""
        test_user = User.objects.create_user(
            username='test_author_created_post',
        )
        self.client.force_login(self.user)
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
                response = self.client.get(name_page)
                post = response.context['page_obj'][
                    self.NUMBER_OF_CONTEXT
                ]
                response = self.client.get(
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
        self.client.force_login(self.user)
        post = Post.objects.create(
            text='пост под кеш',
            author=self.user)
        content_add = self.client.get(
            reverse('posts:index')).content
        post.delete()
        content_delete = self.client.get(
            reverse('posts:index')).content
        self.assertEqual(content_add, content_delete)
        cache.clear()
        content_cache_clear = self.client.get(
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
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_author')
        cls.anon = Client()
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

    def setUp(self):
        cache.clear()

    def test_first_and_second_page_paginate_correct(self):
        """Проверка вывода количества постов на первую и вторую страницы."""
        for pages in self.paginated:
            name, template, arg = pages
            reverse_name = reverse(name, args=arg)
            with self.subTest(reverse_name=reverse_name):
                response = self.anon.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.LIMIT_POSTS,
                    f'Ошибка: Пагинатор не выводит на первую страницу'
                    f'{template} 10 постов',
                )
                response = self.anon.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.NUMBER_OF_POSTS_SECOND_PAGE,
                    f'Ошибка: Пагинатор не выводит на вторую страницу'
                    f'{template} 5 постов',
                )


class FollowViewsTest(TestCase):
    """Устанавливаем данные.

    для тестирования работы

    view-функции отвечающих за работу системы подписки.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post_author = User.objects.create(
            username='post_author',
        )
        cls.post_follower = User.objects.create(
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
        follow = Follow.objects.all().latest('id')
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(follow.author_id, self.post_follower.id)
        self.assertEqual(follow.user_id, self.post_author.id)

    def test_unfollow_on_user(self):
        """Проверка отписки от пользователя."""
        Follow.objects.create(
            user=self.post_author,
            author=self.post_follower)
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
