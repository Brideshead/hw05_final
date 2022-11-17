from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Setinfo(models.Model):
    text = models.TextField(
        'текст поста',
        help_text='Введите текст поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )

    class Meta:
        abstract = True


class TimestampedModel(Setinfo):
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='дата публикации',
    )
    modified = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name='дата изменения',
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Изменяем дату после изменений если дата публикации уже есть."""
        if self.pk:
            self.modified = timezone.now()
        return super(TimestampedModel, self).save(*args, **kwargs)
