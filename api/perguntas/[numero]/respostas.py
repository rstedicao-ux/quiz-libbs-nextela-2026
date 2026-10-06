import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from db import get_db, init_db, json_response, options_response, GABARITO


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        options_response(self)

    def do_POST(self):
        try:
            # Vercel passes dynamic route params as query string: ?numero=3
            qs = parse_qs(urlparse(self.path).query)
            numero = int(qs.get('numero', [None])[0])

            if numero not in GABARITO:
                json_response(self, 422, {"error": "Pergunta inválida"})
                return

            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            usuario_id = str(body['usuario_id'])
            resposta_str = body.get('resposta', '')

            if resposta_str not in ('mito', 'verdade'):
                json_response(self, 422, {"error": "Resposta inválida"})
                return

            init_db()
            conn = get_db()
            cur = conn.cursor()

            # Verificar se usuário existe
            cur.execute('SELECT 1 FROM usuarios WHERE id = %s', (usuario_id,))
            if not cur.fetchone():
                conn.rollback()
                cur.close()
                conn.close()
                json_response(self, 404, {"error": "Participação não encontrada"})
                return

            correta = int(resposta_str == GABARITO[numero])

            # Inserir resposta (ignorar se já respondeu)
            cur.execute(
                'INSERT INTO respostas (usuario_id, pergunta, correta) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING',
                (usuario_id, numero, correta)
            )
            inserted = cur.rowcount

            if inserted and correta:
                cur.execute(
                    'UPDATE contadores SET valor = valor + 1 WHERE nome = %s',
                    (f'pergunta_{numero}_acertos',)
                )

            # Buscar valor real da resposta (pode já ter sido respondida antes)
            cur.execute(
                'SELECT correta FROM respostas WHERE usuario_id = %s AND pergunta = %s',
                (usuario_id, numero)
            )
            correta_real = bool(cur.fetchone()[0])

            # Contar acertos e total de respostas desse usuário
            cur.execute(
                'SELECT SUM(correta), COUNT(*) FROM respostas WHERE usuario_id = %s',
                (usuario_id,)
            )
            acertos, quantidade = cur.fetchone()
            acertos = acertos or 0

            if inserted and quantidade == 6:
                cur.execute(
                    'UPDATE contadores SET valor = valor + 1 WHERE nome = %s',
                    (f'usuarios_com_{acertos}_acertos',)
                )
                cur.execute(
                    "UPDATE contadores SET valor = valor + 1 WHERE nome = 'numero_usuarios'"
                )

            # Buscar todos os contadores
            cur.execute('SELECT nome, valor FROM contadores')
            contadores = {row[0]: row[1] for row in cur.fetchall()}

            # Total de respondentes dessa pergunta
            cur.execute(
                'SELECT COUNT(*) FROM respostas WHERE pergunta = %s',
                (numero,)
            )
            respondentes = cur.fetchone()[0]

            percentual = round(100 * contadores[f'pergunta_{numero}_acertos'] / respondentes) if respondentes else 0

            num_usuarios = contadores.get('numero_usuarios', 0)
            usuarios_com_x = contadores.get(f'usuarios_com_{acertos}_acertos', 0)
            percentil = (
                round(100 * usuarios_com_x / num_usuarios, 2)
                if quantidade == 6 and num_usuarios > 0 else None
            )

            conn.commit()
            cur.close()
            conn.close()

            json_response(self, 200, {
                'correta': correta_real,
                'acertos': acertos,
                'percentual': percentual,
                'percentil': percentil,
                **contadores
            })
        except Exception as e:
            json_response(self, 500, {"error": str(e)})

    def log_message(self, format, *args):
        pass
