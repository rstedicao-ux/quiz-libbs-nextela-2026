from http.server import BaseHTTPRequestHandler
from db import get_db, init_db, json_response, options_response


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        options_response(self)

    def do_GET(self):
        try:
            init_db()
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT valor FROM contadores LIMIT 1")
            cur.fetchone()
            cur.close()
            conn.close()
            json_response(self, 200, {"status": "ok"})
        except Exception as e:
            json_response(self, 500, {"status": "error", "detail": str(e)})

    def log_message(self, format, *args):
        pass
