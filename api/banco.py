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
                    "tabelas": [],
                    "aviso": "Banco de dados ainda não conectado na Vercel."
                })
                return

            init_db()
            cur = conn.cursor()
            tabelas = []
            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
            nomes = [row[0] for row in cur.fetchall()]
            for nome in nomes:
                cur.execute(f'SELECT * FROM "{nome}"')
                colunas = [desc[0] for desc in cur.description]
                registros = [dict(zip(colunas, row)) for row in cur.fetchall()]
                tabelas.append({"nome": nome, "colunas": colunas, "registros": registros})
            cur.close()
            conn.close()
            json_response(self, 200, {"tabelas": tabelas})
        except Exception as e:
            json_response(self, 200, {"tabelas": [], "error": str(e)})

    def log_message(self, format, *args):
        pass
