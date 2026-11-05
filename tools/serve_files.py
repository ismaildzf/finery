import http.server, socketserver, os

ROOT = os.path.abspath("versions")
os.chdir(ROOT)

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        super().end_headers()

    def log_message(self, *args):
        pass

with socketserver.TCPServer(("127.0.0.1", 8765), Handler) as httpd:
    httpd.serve_forever()
