import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus
from mixer.backend.django import mixer

from posts.models import Group, Post, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = 'media/posts'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """
    Устанавливаем данные для тестирования posts/forms.
    """

    @classmethod
    def setUpClass(cls: TestCase):
        """
        Создаём тестовую запись в БД
        и сохраняем созданную запись в качестве переменной класса.
        """
        super().setUpClass()
        cls.anon = Client()
        cls.client_author = Client()
        cls.user = User.objects.create_user(username='test_author')
        cls.user_not_author = User.objects.create(username='not_author')
        cls.client_author.force_login(cls.user)
        cls.client_not_author = Client()
        cls.group = mixer.blend(Group)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_auth_user_create_post_ok(self): 
        """Проверка создания поста для авторизованного пользователя."""
        posts_count = Post.objects.count() 
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
        response = self.client_author.post( 
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
        self.assertEqual(response.status_code, HTTPStatus.OK) 
        self.assertEqual(Post.objects.count(), posts_count + 1) 
        self.assertEqual(Post.objects.latest('pk').text, 'Тестовый пост') 
        self.assertEqual(Post.objects.latest('pk').author, self.user) 
        self.assertEqual(Post.objects.latest('pk').group.pk, self.group.pk)
        self.assertEqual(Post.objects.latest('pk').image, 'posts/small.gif')

    def test_anon_cannot_create_post(self):
        """Проверка создания записи не авторизированным пользователем."""
        self.assertEqual(Post.objects.count(), 0)
        response = self.anon.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост',
                'group': self.group.pk,
                'author': self.anon,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            '/auth/login/?next=/create/',
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_auth_user_create_comment(self):
        """Проверка создания комментария авторизированным пользователем."""
        self.assertEqual(Comment.objects.count(), 0)
        comments_count = Comment.objects.count()
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.user,
        )
        response = self.client_author.post(
            reverse(
                'posts:add_comment',
                args=(post.pk,),
            ),
            {'text': 'Тестовый комментарий'},
            follow=True,
        )
        comment = Comment.objects.latest('pk')
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(comment.text == 'Тестовый комментарий')
        self.assertTrue(comment.author == self.user)
        self.assertTrue(comment.pk == post.pk)
        self.assertRedirects(
            response, 
            reverse('posts:post_detail', args=(post.pk,)),
        )

    def test_nonauth_user_create_comment(self):
        """Проверка создания комментария не авторизированным пользователем."""
        self.assertEqual(Comment.objects.count(), 0)
        comments_count = Comment.objects.count()
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.user,
        )
        response = self.anon.post(
            reverse(
                'posts:add_comment',
                args=(post.pk,)),
            {'text': 'Тестовый комментарий'},
            follow=True,
        )
        redirect = reverse('login') + '?next=' + reverse(
            'posts:add_comment', args=(post.pk,))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertRedirects(response, redirect)    

    def test_auth_user_edit_post_ok(self):
        """Проверка редактирования записи авторизированным клиентом."""
        post = mixer.blend( 
            'posts.Post',
            text='Отредактированный текст поста',
            author=self.user,
        ) 
        response = self.client_author.post(
            reverse(
                'posts:post_edit',
                args=(post.pk,),
            ),
            {
                'text': 'Отредактированный текст поста',
                'group': self.group.pk,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            post.text == 'Отредактированный текст поста',
        )

    def test_client_not_auth_cannot_edit(self):
        """
        Проверка, что пост не редактируется авторизованным
        пользователем - не автором поста.
        """
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.user,
            group=self.group,
        )
        response = self.client_not_author.post(
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
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('pk')
        self.assertFalse(post.text == 'Тестовый пост')
        self.assertTrue(post.author == self.user)
        self.assertTrue(post.group.pk == self.group.pk)

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
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse('login')
            + '?next='
            + reverse(
                'posts:post_edit',
                args=(post.pk,),
            ),
        )
