from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from mixer.backend.django import mixer

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    """Устанавливаем данные для тестирования модели Post."""

    @classmethod
    def setUpClass(cls):
        """Создаём тестовую запись в БД.

        Сохраняем созданную запись в качестве переменной класса.
        """
        super().setUpClass()

        cls.user = User.objects.create_user(username='test_author')

        cls.group = mixer.blend(Group)

    def test_model_post_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        self.assertEqual(str(self.group), self.group.title)

    def test_model_post_first_15_symbols(self):
        """Проверяем, первые 15 символов выводимые для Post в __str__."""
        self.post = Post.objects.create(
            author=self.user,
            text='test_text',
        )
        self.assertEqual(
            str(self.post)[:settings.LENGTH_POST],
            self.post.text,
        )


class GroupModelTest(TestCase):
    """Устанавливаем данные для тестирования модели Group."""

    @classmethod
    def setUpClass(cls):
        """Создаём тестовую запись в БД.

        Сохраняем созданную запись в качестве переменной класса.
        """
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_author')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_text',
        )

    def test_model_group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        self.assertEqual(str(self.group), self.group.title)

    def test_model_group_first_15_symbols(self):
        """Проверяем, первые 15 символов выводимые для Group в __str__."""
        self.assertEqual(
            str(self.group.title)[:settings.TITLE_LENGTH_RETURN],
            self.group.title,
        )
