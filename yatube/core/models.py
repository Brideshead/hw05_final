from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Setinfo(models.Model):
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
