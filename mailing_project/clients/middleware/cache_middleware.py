from django.utils.cache import patch_cache_control


class ClientCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Кэшируем только GET-запросы для анонимных пользователей или статических страниц
        if request.method == 'GET' and not request.user.is_authenticated:
            # Кэшируем на 1 час для анонимных пользователей
            patch_cache_control(response, max_age=3600, public=True)
        elif request.path.startswith('/static/'):
            # Кэшируем статические файлы на 24 часа
            patch_cache_control(response, max_age=86400, public=True, immutable=True)

        return response
