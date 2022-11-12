from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from core.utils import paginate
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User


@cache_page(20, key_prefix='index_page')
def index(request: HttpRequest) -> HttpResponse:
    """Отрисовка главной страницы с 10 последними статьями.

    Принимает WSGIRequest и возвращает подготовленную
    html страницу с данными.
    """
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': paginate(
                request,
                Post.objects.select_related('author', 'group'),
                settings.LIMIT_POSTS,
            ),
        },
    )


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """Отрисовка страницы группы с 10 последними статьями данной группы.

    Принимает WSGIRequest, наименование группы в формате slug
    и возвращает подготовленную html страницу с данными.
    """
    return render(
        request,
        'posts/group_list.html',
        {
            'group': get_object_or_404(Group, slug=slug),
            'page_obj': paginate(
                request,
                get_object_or_404(
                    Group,
                    slug=slug,
                ).posts.select_related('group'),
                settings.LIMIT_POSTS,
            ),
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Отрисовка страницы профиля пользователя.

    С информацией обо всех постах данного пользователя.
    """
    return render(
        request,
        'posts/profile.html',
        {
            'page_obj': paginate(
                request,
                get_object_or_404(
                    User,
                    username=username,
                ).posts.select_related('author'),
                settings.LIMIT_POSTS,
            ),
            'author': get_object_or_404(User, username=username),
        },
    )


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Отрисовка страницы с описанием конкретного выбранного поста."""
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': get_object_or_404(Post, pk=pk),
            'form': CommentForm(),
        },
    )


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Отрисовка страницы с окном создания поста.

    Можно указать текст поста и выбрать группу,
    к которой данный пост будет относиться.

    Посты могут создавать только авторизованные пользователи.
    """
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            {
                'form': form,
                'is_edit': False,
            },
        )
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', form.instance.author)


@login_required
def post_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """Отрисовка страницы для редактирования уже созданного поста.

    Пост может редактировать только авторизованный пользователь.
    Редактировать можно только свои посты.
    """
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('posts:post_detail', pk)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', pk)

    return render(
        request, 'posts/create_post.html', {'form': form, 'is_edit': True},
    )


@login_required
def add_comment(request: HttpRequest, pk: int) -> HttpResponse:
    """Отрисовка страницы для добавления комментария к посту.

    Комментарий может оставлять только
    авторизованный пользователь.
    """
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
    return redirect('posts:post_detail', pk)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    """Отрисовка страницы c инф. о подписках текущего пользователя."""
    return render(
        request,
        'posts/follow.html',
        {
            'page_obj': paginate(
                request,
                Post.objects.filter(
                    author__following__user=request.user,
                ),
                settings.LIMIT_POSTS,
            ),
        },
    )


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    """Подписаться на автора в его профиле."""
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    """Отписаться  от автора в его профиле."""
    get_object_or_404(
        Follow,
        user=request.user,
        author__username=username,
    ).delete()
    return redirect('posts:profile', username)
