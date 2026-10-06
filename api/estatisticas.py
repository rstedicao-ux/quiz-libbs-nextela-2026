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
            cur.execute("SELECT nome, valor FROM contadores")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            json_response(self, 200, {row[0]: row[1] for row in rows})
        except Exception as e:
            json_response(self, 500, {"error": str(e)})

    def log_message(self, format, *args):
        pass
