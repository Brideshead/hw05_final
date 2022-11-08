from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    """
    Вывод шаблона с ошибкой 404 в случае если страница не найдена.
    """
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def permission_denied(request: HttpRequest, exception) -> HttpResponse:
    """
    Вывод шаблона с ошибкой 403 в случае если страница не найдена.
    """
    return render(request, 'core/403.html', status=403)


def csrf_failure(request: HttpRequest) -> HttpResponse:
    """403: ошибка проверки CSRF, запрос отклонён."""
    return render(request, 'core/403csrf.html')


def server_error(request: HttpRequest) -> HttpResponse:
    """
    Вывод шаблона с ошибкой 500 в случае если страница не найдена.
    """
    return render(request, 'core/500.html', status=500)
