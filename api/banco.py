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
            json_response(self, 500, {"error": str(e)})

    def log_message(self, format, *args):
        pass
