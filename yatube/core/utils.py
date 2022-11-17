from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpRequest


def paginate(
    request: HttpRequest,
    queryset: list,
    posts_limit: int = settings.LIMIT_POSTS,
) -> None:
    """Функция постраничного разделения.

    В зависимости от объемов входящей информации,
    вынесена в отдельную область.
    """
    return Paginator(queryset, posts_limit).get_page(request.GET.get('page'))
