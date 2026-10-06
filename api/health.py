import os
import sys
from http.server import BaseHTTPRequestHandler

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for p in [current_dir, parent_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from db import get_db, init_db, json_response, options_response, get_postgres_url
except ImportError:
    from api.db import get_db, init_db, json_response, options_response, get_postgres_url


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        options_response(self)

    def do_GET(self):
        try:
            db_url = get_postgres_url()
            if not db_url:
                json_response(self, 200, {
                    "status": "ok",
                    "database": "not_configured",
                    "message": "Vercel Postgres URL não configurada. O quiz roda em modo local/fallback."
                })
                return

            init_db()
            conn = get_db()
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT valor FROM contadores LIMIT 1")
                cur.fetchone()
                cur.close()
                conn.close()
                json_response(self, 200, {"status": "ok", "database": "connected"})
            else:
                json_response(self, 200, {
                    "status": "ok",
                    "database": "connecting_failed",
                    "message": "Banco de dados inacessível no momento."
                })
        except Exception as e:
            json_response(self, 200, {"status": "ok", "database": "error", "detail": str(e)})

    def log_message(self, format, *args):
        pass
