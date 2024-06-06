import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

class Redirect(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.protocol_version = "HTTP/1.1"
        self.send_response(101)
        self.end_headers()


HTTPServer(("", 1234), Redirect).serve_forever()
