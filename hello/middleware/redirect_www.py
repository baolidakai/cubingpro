from django.http import HttpResponsePermanentRedirect

class RedirectToWWWMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        return self.get_response(request)
