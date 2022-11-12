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


# не могу взять данные из core.models Setinfo
# у меня летят миграции и валится пайтест
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
        verbose_name='дата публикации',
        auto_now_add=True,
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
        """Возвращает в консоль сокращенный текст поста."""
        return self.text[:settings.TEXT_LENGTH_RETURN]


class Comment(models.Model):
    """
    Модель для хранения комментариев.

    post: данные о посте, установлена связь с таблицей Post,
    при удалении из таблицы Post поста,
    также будут удалены все связанные комментарии.
    author: автор статьи, установлена связь с таблицей User,
    при удалении из таблицы User автора,
    также будут удалены все связанные комментарии.
    text: текст комменатария.
    created: дата создания комментария.
    updated: дата обновления комментария.
    active: статус комментария.
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    text = models.TextField(
        'текст',
        help_text='Введите текст',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='создан',
    )
    updated = models.DateTimeField(
        auto_now_add=True,
        verbose_name='обновлен',
    )
    active = models.BooleanField(
        default=True,
        verbose_name='активен',
    )

    class Meta:
        default_related_name = 'comments'
        ordering = ('-pub_date',)
        verbose_name_plural = 'комментарии'
        verbose_name = 'комментарий'

    def __str__(self) -> str:
        return self.text[:settings.LENGTH_POST]


class Follow(models.Model):
    """
    Модель для хранения данных о подписках.

    user: данные о пользователе, установлена связь с таблицей User,
    при удалении из таблицы User пользователя,
    также будут удалены все связанные подписки.
    author: автор статьи, установлена связь с таблицей User,
    при удалении из таблицы User автора,
    также будут удалены все связанные подписки.
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
        verbose_name_plural = 'подписки'
        verbose_name = 'подписка'

    def __str__(self) -> str:
        return f'{self.user} подписался на {self.author}'
