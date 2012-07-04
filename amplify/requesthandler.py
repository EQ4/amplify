import mimetypes
import os
import re
import shutil
import socket

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn


class Request:
    pass


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class HttpResponse:
    def __init__(self, content, status_code=200, content_type='text/html',
            content_length=0, headers=None):
        self.content = content
        self.status_code = status_code
        self.content_type = content_type
        self.content_length = content_length or len(content)
        self.headers = headers or {}


def parse_range(range_string):
    match = re.match(r'^(?P<unit>bytes)=(?P<start>\d+)-(?P<end>\d+)?$', range_string)

    if not match:
        raise ValueError("Couldn't parse Content-Range value")

    groups = match.groupdict()

    return (int(groups['start']),
            int(groups['end']) if groups['end'] else 0)


class RequestHandler(BaseHTTPRequestHandler):
    static_url_prefix = '/static/'
    static_dir = 'static'

    def log_message(self, *args, **kwargs):
        pass

    def sanitize_static_path(self, path):
        sanitized_path = ''

        for part in path.split('/'):
            if not part:
                continue

            if part in (os.curdir, os.pardir):
                continue

            sanitized_path = os.path.join(sanitized_path, part)

        return sanitized_path

    def do_GET(self):
        if self.path.startswith(self.static_url_prefix):
            # FIXME: The path to the static files should only be fetched ONCE.
            root_path = os.path.dirname(os.path.abspath(__file__))

            # Strip the static url prefix to get the relative path.
            path = self.path[len(self.static_url_prefix):]

            # Sanitize the path to prevent a malicious client to wander up the
            # directory tree.
            path = self.sanitize_static_path(path)
            full_path = os.path.join(root_path, self.static_dir, path)

            if not os.path.exists(full_path):
                self.send_response_only(404)
                return

            if os.path.isdir(full_path):
                self.send_response_only(404, 'Directory indexes are not allowed.')
                return

            if not os.access(full_path, os.R_OK):
                self.send_response_only(403)
                return

            content_type, _content_encoding = mimetypes.guess_type(full_path)
            if content_type is None:
                content_type = 'application/octet-stream'

            content_length = os.stat(full_path).st_size
            content_start = 0

            # Respect the Range-header.
            range_requested = self.headers['range']
            if range_requested:
                # Partial Content
                self.send_response(206)

                range_start, _range_end = parse_range(range_requested)
                content_start = range_start

                self.send_header(
                    'Content-Range', 'bytes {0}-{1}/{2}'.format(
                        range_start,
                        content_length - 1,
                        content_length
                    )
                )

                self.send_header('Content-Length', content_length - range_start)

            else:
                self.send_response(200)
                self.send_header('Content-Length', content_length)

            self.send_header('Content-Type', content_type)
            self.end_headers()

            # Finally, we can send our file.
            with open(full_path, 'rb') as file:
                file.seek(content_start, 0)
                shutil.copyfileobj(file, self.wfile)

            return

        # Populate the request object
        request = Request()
        request.method = self.command
        request.path = self.path
        request.headers = self.headers
        request.album = None # We'll set this later

        # Routing
        view, args, kwargs = None, None, None

        for url_pattern, handler in self.url_map.items():
            url_pattern = '^{0}$'.format(url_pattern)
            match = re.match(url_pattern, request.path)

            if match:
                view, args, kwargs = handler, match.groups(), match.groupdict()

        # No view to be found? Raise 404
        if not view:
            self.send_response_only(404)

        else:
            # Get the response from the view function
            response = view(request, *args, **kwargs)

            if isinstance(response, str):
                response = HttpResponse(response.encode('utf-8'))

            self.send_response(response.status_code)

            for header, value in response.headers.items():
                self.send_header(header, value)

            self.send_header('Content-Type', response.content_type)
            self.send_header('Content-Length', response.content_length)
            self.end_headers()

            try:
                self.wfile.write(response.content)
            except socket.error:
                pass
