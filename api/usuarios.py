import json
from http.server import BaseHTTPRequestHandler
from db import get_db, init_db, json_response, options_response


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        options_response(self)

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            usuario_id = str(body['usuario_id'])

            init_db()
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO usuarios (id) VALUES (%s) ON CONFLICT (id) DO NOTHING',
                (usuario_id,)
            )
            cur.execute(
                "SELECT valor FROM contadores WHERE nome = 'numero_usuarios'"
            )
            total = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            json_response(self, 200, {'usuario_id': usuario_id, 'numero_usuarios': total})
        except Exception as e:
            json_response(self, 500, {"error": str(e)})

    def log_message(self, format, *args):
        pass
