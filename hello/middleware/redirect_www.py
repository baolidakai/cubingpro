from django.http import HttpResponsePermanentRedirect

class RedirectToWWWMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if host == 'cubingpro.com':
            return HttpResponsePermanentRedirect(
                f'https://www.cubingpro.com{request.get_full_path()}'
            )
        return self.get_response(request)
