import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Comment, Group, Post

User = get_user_model()


@override_settings(MEDIA_ROOT=settings.TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """Устанавливаем данные для тестирования posts/forms."""

    @classmethod
    def setUpClass(cls: TestCase):
        """Создаём тестовую запись в БД.

        Сохраняем созданную запись в качестве переменной класса.
        """
        super().setUpClass()

        cls.anon = Client()
        cls.client = Client()

        cls.user = User.objects.create_user(username='test_author')
        cls.client.force_login(cls.user)

        cls.group = mixer.blend(Group)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_auth_user_create_post_ok(self):
        """Проверка создания поста для авторизованного пользователя."""
        self.client.force_login(self.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif',
        )
        response = self.client.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост',
                'group': self.group.pk,
                'image': self.uploaded,
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
        post = Post.objects.latest('pk')
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.text, 'Тестовый пост')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.pk, self.group.pk)
        self.assertEqual(post.image, 'posts/small.gif')

    def test_anon_cannot_create_post(self):
        """Проверка создания записи не авторизированным пользователем."""
        self.anon.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост',
                'group': self.group.pk,
                'author': self.anon,
            },
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_auth_user_create_comment(self):
        """Проверка создания комментария авторизированным пользователем."""
        self.client.force_login(self.user)
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.user,
        )
        response = self.client.post(
            reverse(
                'posts:add_comment',
                args=(post.pk,),
            ),
            {
                'text': 'Тестовый комментарий',
            },
            follow=True,
        )
        comment = Comment.objects.latest('id')
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.text, 'Тестовый комментарий')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.pk, post.pk)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(post.pk,)),
        )

    def test_nonauth_user_create_comment(self):
        """Проверка создания комментария не авторизированным пользователем."""
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.user,
        )
        self.anon.post(
            reverse(
                'posts:add_comment',
                args=(post.pk,)),
            {
                'text': 'Тестовый комментарий',
            },
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), 0)

    def test_user_post_author_edit_post_ok(self):
        """Проверка редактирования записи авторизированным клиентом."""
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif',
        )
        post = mixer.blend(
            'posts.Post',
            text='Отредактированный текст поста',
            author=self.user,
        )
        self.client.post(
            reverse(
                'posts:post_edit',
                args=(post.pk,),
            ),
            {
                'text': 'Отредактированный текст поста',
                'group': self.group.pk,
                'image': self.uploaded,
            },
            follow=True,
        )
        self.assertEqual(
            post.text,
            'Отредактированный текст поста',
        )
        self.assertEqual(post.image, 'posts/image.gif')

    def test_client_not_auth_cannot_edit(self):
        """Проверка, что пост не редактируется не автором поста."""
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.user,
            group=self.group,
        )
        post = Post.objects.latest('pk')
        self.assertNotEqual(post.text, 'Тестовый пост')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.pk, self.group.pk)

    def test_anon_user_cannot_edit(self):
        """Проверка редактирования поста неавторизованным пользователем."""
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.user,
            group=self.group,
        )
        response = self.anon.post(
            reverse(
                'posts:post_edit',
                args=(post.pk,),
            ),
            {
                'text': 'Тестовый пост',
                'group': self.group.pk,
            },
            follow=True,
        )
        self.assertEqual(
            post.text,
            'Текст поста для редактирования',
        )
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)
        self.assertRedirects(
            response,
            reverse('login')
            + '?next='
            + reverse(
                'posts:post_edit',
                args=(post.pk,),
            ),
        )
