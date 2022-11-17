from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from core.models import TimestampedModel

User = get_user_model()


class Group(models.Model):
    """
    Модель для хранения данных сообществ.

    title: название группы.
    slug: уникальный адрес группы, часть URL.
    description: текст, описывающий сообщество.
    """

    title = models.CharField('название группы', max_length=200)
    slug = models.SlugField('уникальный адрес', unique=True)
    description = models.TextField('описание группы')

    def __str__(self) -> str:
        """Возвращает в консоль сокращенное название группы."""
        return (
            self.title[:settings.TITLE_LENGTH_RETURN]
            if len(self.title) > settings.TITLE_LENGTH_RETURN
            else self.title
        )


class Post(TimestampedModel):
    """
    Модель для хранения статей.

    Наследует из TimestampedModel:
    text: текст.
    pud_date: дата публикации статьи.
    author: автор статьи, установлена связь с таблицей User,
    при удалении из таблицы User автора,
    также будут удалены все связанные статьи.

    Дополнительные поля:
    group: название сообщества, к которому относится статья,
    установлена связь с моделью Group, чтобы при добавлении
    новой записи можно было сослаться на данную модель.
    """

    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def __str__(self) -> str:
        """Возвращает в консоль сокращенный текст поста."""
        return (
            self.text[:settings.TEXT_LENGTH_POST_RETURN]
            if len(self.text) > settings.TEXT_LENGTH_POST_RETURN
            else self.text
        )


class Comment(TimestampedModel):
    """
    Модель для хранения комментариев.

    Наследует из TimestampedModel:
    text: текст.
    pud_date: дата добавления комментария.
    author: автор статьи, установлена связь с таблицей User,
    при удалении из таблицы User автора,
    также будут удалены все связанные комментарии.

    Дополнительные поля:
    post: данные о посте, установлена связь с таблицей Post,
    при удалении из таблицы Post поста,
    также будут удалены все связанные комментарии.
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='пост',
    )

    class Meta:
        default_related_name = 'comments'
        ordering = ('-pub_date',)
        verbose_name_plural = 'комментарии'
        verbose_name = 'комментарий'

    def __str__(self) -> str:
        """Возвращает в консоль сокращенный текст комментария."""
        return (
            self.text[:settings.SHORT_TEXT_RETURN]
            if len(self.text) > settings.SHORT_TEXT_RETURN
            else self.text
        )


class Follow(models.Model):
    """
    Модель для хранения данных о подписках.

    user: данные о пользователе, установлена связь с таблицей User,
    при удалении из таблицы User пользователя,
    также будут удалены все связанные подписки.
    author: автор статьи, установлена связь с таблицей User,
    при удалении из таблицы User автора,
    также будут удалены все связанные подписки.
    Пользователь не может подписывать на себя или
    на одного того же автора два раза.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='user_author_pair_unique',
                fields=['user', 'author'],
            ),
            models.CheckConstraint(
                name='user_prevent_self_follow',
                check=~models.Q(author=models.F('user')),
            ),
        ]
        verbose_name_plural = 'подписки'
        verbose_name = 'подписка'

    def __str__(self) -> str:
        """Возвращает в консоль текст о новом подписчике."""
        return f'{self.user} подписался на {self.author}'
