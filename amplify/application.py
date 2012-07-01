import functools
import os

from amplify.requesthandler import RequestHandler, ThreadingHTTPServer


class Application:
    requesthandler = RequestHandler
    httpserver = ThreadingHTTPServer

    def __init__(self, import_name):
        self.url_map = {}
        # self.root_path = os.path.dirname(os.path.abspath(__name__))

    def route(self, url):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(request, *args, **kwargs):
                request.album = self.album
                request.cover = self.cover

                return func(request, *args, **kwargs)

            self.url_map[url] = wrapper

            return wrapper

        return decorator

    def run(self, bind, port, songs):
        self.album = songs
        self.requesthandler.url_map = self.url_map

        httpd = self.httpserver((bind, port), self.requesthandler)
        httpd.serve_forever()


