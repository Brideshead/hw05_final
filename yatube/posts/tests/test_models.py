from django.test import TestCase
from mixer.backend.django import mixer


class PostModelTest(TestCase):
    """Тестируем post/models, модель Post.

    Проверяем что у модели Post корректно выводятся данные в консоль.
    """

    @classmethod
    def setUpClass(cls):
        """Создаём тестовый пост в БД."""
        super().setUpClass()

        cls.post = mixer.blend(
            'posts.Post',
            text='текст поста',
        )

    def test_model_post_have_correct_object_name(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        self.assertEqual(
            str(self.post),
            self.post.text,
        )


class GroupModelTest(TestCase):
    """Тестируем post/models, модель Group.

    Проверяем что у модели Group данные корректно выводятся в консоль.
    """
    @classmethod
    def setUpClass(cls):
        """Создаём тестовую группу в БД."""
        super().setUpClass()

        cls.group = mixer.blend('posts.Group')

    def test_model_group_have_correct_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        self.assertEqual(str(self.group), self.group.title)
