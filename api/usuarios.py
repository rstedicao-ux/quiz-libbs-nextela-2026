import json
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

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            usuario_id = str(body.get('usuario_id', 'anon'))

            conn = get_db()
            if conn:
                try:
                    init_db()
                    cur = conn.cursor()
                    cur.execute(
                        'INSERT INTO usuarios (id) VALUES (%s) ON CONFLICT (id) DO NOTHING',
                        (usuario_id,)
                    )
                    cur.execute(
                        "SELECT valor FROM contadores WHERE nome = 'numero_usuarios'"
                    )
                    row = cur.fetchone()
                    total = row[0] if row else 1
                    conn.commit()
                    cur.close()
                    conn.close()
                    json_response(self, 200, {'usuario_id': usuario_id, 'numero_usuarios': total})
                    return
                except Exception as ex:
                    print(f"Erro ao salvar usuario no Postgres: {ex}")
                    try:
                        conn.close()
                    except Exception:
                        pass

            # Fallback seguro caso o banco ainda não esteja configurado
            json_response(self, 200, {'usuario_id': usuario_id, 'numero_usuarios': 1, 'modo': 'local'})
        except Exception as e:
            json_response(self, 200, {'usuario_id': 'local', 'numero_usuarios': 1, 'modo': 'fallback'})

    def log_message(self, format, *args):
        pass
