import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer
from posts.models import Comment, Group, Post
from posts.tests.common import image

User = get_user_model()


@override_settings(MEDIA_ROOT=settings.TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """Тестирования posts/forms.

    В данном тесте делаем проверки на:
    Что автозированный пользователь может создать пост.
    Что неавтозированный пользователь не может создать пост.
    Что автозированный пользователь может создать коммент.
    Что неавтозированный пользователь не может создать коммент.
    Что автозированный пользователь-автор поста может редактировать пост.
    Что пост не редактируется не автором поста.
    Что неавтозированный пользователь не может редактировать пост.
    """

    @classmethod
    def setUpClass(cls: TestCase):
        """Создаём данные для тестов и логиним."""

        super().setUpClass()

        cls.user = User.objects.create_user(username='test_author')
        cls.user_not_author = User.objects.create_user(username='no_author')
        cls.group = mixer.blend(Group)

        cls.anon = Client()
        cls.client_author = Client()
        cls.client_not_author = Client()
        cls.client_author.force_login(cls.user)
        cls.client_not_author.force_login(cls.user_not_author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def test_auth_user_create_post_ok(self):
        """Проверка что авт. пользователь может создать пост."""
        self.assertEqual(Post.objects.count(), 0)
        response = self.client_author.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост',
                'group': self.group.id,
                'image': image(),
            },
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                args=(self.user.username,),
            ),
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        self.assertEqual(post.text, 'Тестовый пост')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group_id, self.group.id)
        self.assertEqual(post.image, 'posts/giffy.gif')

    def test_anon_cannot_create_post_denied(self):
        """Проверка что неавт. пользователь не может создать пост."""
        self.anon.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост',
                'group': self.group.id,
            },
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_auth_user_create_comment_ok(self):
        """Проверка что авт. пользователь может создать коммент."""
        post = mixer.blend(
            'posts.Post',
            text='Текст поста для редактирования',
            author=self.user,
        )
        response = self.client_author.post(
            reverse(
                'posts:add_comment',
                args=(post.id,),
            ),
            {
                'text': 'Тестовый комментарий',
            },
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.get()
        self.assertEqual(comment.text, 'Тестовый комментарий')
        self.assertEqual(comment.author, self.user)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(post.id,)),
        )

    def test_nonauth_user_create_comment_denied(self):
        """Проверка что неавт. пользователь не может создать коммент."""
        post = mixer.blend(
            'posts.Post',
            text='Текст поста для редактирования',
            author=self.user,
        )
        self.anon.post(
            reverse(
                'posts:add_comment',
                args=(post.id,)),
            {
                'text': 'Тестовый комментарий',
            },
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), 0)

    def test_user_post_author_edit_post_ok(self):
        """Проверка что авт. пользов.-автор поста может редактировать пост."""
        post = mixer.blend(
            'posts.Post',
            text='Текст поста',
            author=self.user,
        )
        self.client_author.post(
            reverse(
                'posts:post_edit',
                args=(post.id,),
            ),
            {
                'text': 'Отредактированный текст поста',
                'group': self.group.id,
                'image': image(),
            },
            follow=True,
        )
        post_changed = Post.objects.get()
        self.assertEqual(
            post_changed.text,
            'Отредактированный текст поста',
        )
        self.assertNotEqual('posts/giffy.gif', post.image)
        self.assertEqual(post_changed.group_id, self.group.id)

    def test_client_not_auth_edit_denied(self):
        """Проверка, что пост не редактируется не автором поста."""
        post = mixer.blend(
            'posts.Post',
            author=self.user,
        )
        self.client_not_author.post(
            reverse(
                'posts:post_edit',
                args=(post.id,),
            ),
            {
                'text': 'Отредактированный текст поста',
                'group': self.group.id,
                'image': image(),
            },
            follow=True,
        )
        post_control = Post.objects.get()
        self.assertEqual(post_control.text, post.text)
        self.assertEqual(post_control.author, post.author)
        self.assertEqual(post_control.group_id, post.group)
        self.assertEqual(post_control.image, post.image)

    def test_anon_user_edit_denied(self):
        """Проверка что неавт. пользователь не может редактировать пост."""
        post = mixer.blend(
            'posts.Post',
            text='Текст поста для редактирования',
            author=self.user,
            group=self.group,
        )
        self.anon.post(
            reverse(
                'posts:post_edit',
                args=(post.id,),
            ),
            {
                'text': 'Тестовый пост',
            },
            follow=True,
        )
        self.assertEqual(
            post.text,
            'Текст поста для редактирования',
        )
        self.assertEqual(post.author, self.user)
