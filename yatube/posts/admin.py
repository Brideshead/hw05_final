from core.admin import BaseAdmin
from django.contrib import admin
from posts.models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(BaseAdmin):
    """
    Настройки отображения модели 'Статьи' в интерфейсе админки.

    list_display: перечисляем поля, которые должны отображаться.
    list_editable: опция для измнения поля group в любом посте.
    search_fields: интерфейс для поиска по тексту постов.
    list_filter: фильтрация по дате.
    empty_value_display: вывод в поле текста '-пусто',
    если информация отсутствует.
    """

    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)


@admin.register(Group)
class GroupAdmin(BaseAdmin):
    """
    Настройки отображения модели 'Группы' в интерфейсе админки.

    list_display: перечисляем поля, которые должны отображаться.
    list_editable: опция для измнения поля заголовка в любом посте.
    search_fields: интерфейс для поиска группы по уникальному номеру.
    list_filter: фильтрация по заголовку.
    empty_value_display: вывод в поле текста '-пусто',
    если информация отсутствует.
    """

    list_display = ('pk', 'title')
    list_editable = ('title',)
    list_filter = ('title',)
    search_fields = ('pk',)


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = ('post', 'author', 'text', 'pub_date')
    list_filter = ('text', 'pub_date')
    search_fields = ('post', 'author', 'text')


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')
