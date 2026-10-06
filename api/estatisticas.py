import os
import sys
from http.server import BaseHTTPRequestHandler

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for p in [current_dir, parent_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from db import get_db, init_db, json_response, options_response
except ImportError:
    from api.db import get_db, init_db, json_response, options_response


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        options_response(self)

    def do_GET(self):
        try:
            conn = get_db()
            if not conn:
                json_response(self, 200, {
                    "numero_usuarios": 0,
                    "aviso": "Banco de dados ainda não conectado na Vercel."
                })
                return

            init_db()
            cur = conn.cursor()
            cur.execute("SELECT nome, valor FROM contadores")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            json_response(self, 200, {row[0]: row[1] for row in rows})
        except Exception as e:
            json_response(self, 200, {"numero_usuarios": 0, "error": str(e)})

    def log_message(self, format, *args):
        pass
