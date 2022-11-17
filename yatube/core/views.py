from http import HTTPStatus

from django.http import (HttpRequest, HttpResponseForbidden,
                         HttpResponseNotFound, HttpResponseServerError)
from django.shortcuts import render


# тест проходит только с таким exception
# c *args и без аргументы тест не проходит
def page_not_found(request: HttpRequest, exception) -> HttpResponseNotFound:
    """Вывод шаблона с ошибкой 404 в случае если страница не найдена."""
    return render(
        request,
        'core/404.html',
        {
            'path': request.path,
        },
        status=HTTPStatus.NOT_FOUND.value,
    )


def permission_denied(
        request: HttpRequest, *args: tuple) -> HttpResponseForbidden:
    """Вывод шаблона с 403 в случае если страница не найдена."""
    return render(
        request,
        'core/403.html',
        HTTPStatus.FORBIDDEN.value,
    )


def csrf_failure(request: HttpRequest) -> HttpResponseForbidden:
    """403: ошибка проверки CSRF, запрос отклонён."""
    return render(request, 'core/403csrf.html')


def server_error(request: HttpRequest) -> HttpResponseServerError:
    """Вывод шаблона с ошибкой 500 в случае если страница не найдена."""
    return render(
        request,
        'core/500.html',
        HTTPStatus.INTERNAL_SERVER_ERROR.value,
    )
