from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

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
        return self.title[:settings.TITLE_LENGTH_RETURN]


class Post(models.Model):
    """
    Модель для хранения статей.

    text: текс статьи.
    pud_date: дата публикации статьи.
    author: автор статьи, установлена связь с таблицей User,
    при удалении из таблицы User автора,
    также будут удалены все связанные статьи.
    group: название сообщества, к которому относится статья,
    установлена связь с моделью Group, чтобы при добавлении
    новой записи можно было сослаться на данную модель.
    """

    text = models.TextField(
        'текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации', auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
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
        """
        Возвращает в консоль сокращенный текст поста.
        """
        return self.text[:settings.TEXT_LENGTH_RETURN]


class Comment(models.Model):
    """
    Модель для хранения комментариев.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор',
    )
    text = models.TextField(
        verbose_name='комментарий',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='создан',
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name='обновлен',
    )
    active = models.BooleanField(
        default=True,
        verbose_name='активен',
    )

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = 'комментарии'
        verbose_name = 'комментарий'

    def __str__(self):
        return self.text[:15]

class Follow(models.Model):
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
        verbose_name_plural = 'подписки'
        verbose_name = 'подписка'

    def __str__(self):
        return f'{self.user} подписался на {self.author}'

        