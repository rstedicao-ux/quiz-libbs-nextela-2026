import os
import psycopg2
import psycopg2.extras

GABARITO = {1: 'mito', 2: 'verdade', 3: 'mito', 4: 'mito', 5: 'mito', 6: 'verdade'}


def get_db():
    conn = psycopg2.connect(os.environ['POSTGRES_URL'])
    conn.autocommit = False
    return conn


def init_db():
    """Create tables and seed counters if they don't exist."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS contadores (
            nome TEXT PRIMARY KEY,
            valor INTEGER NOT NULL DEFAULT 0
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS respostas (
            usuario_id TEXT NOT NULL REFERENCES usuarios(id),
            pergunta INTEGER NOT NULL CHECK(pergunta BETWEEN 1 AND 6),
            correta INTEGER NOT NULL CHECK(correta IN (0, 1)),
            PRIMARY KEY (usuario_id, pergunta)
        )
    ''')
    nomes = ['numero_usuarios'] + [f'pergunta_{i}_acertos' for i in GABARITO] + \
            [f'usuarios_com_{s}_acertos' for s in range(7)]
    for nome in nomes:
        cur.execute(
            'INSERT INTO contadores (nome, valor) VALUES (%s, 0) ON CONFLICT (nome) DO NOTHING',
            (nome,)
        )
    conn.commit()
    cur.close()
    conn.close()


def json_response(handler, status, body):
    import json
    encoded = json.dumps(body, ensure_ascii=False).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type')
    handler.end_headers()
    handler.wfile.write(encoded)


def options_response(handler):
    handler.send_response(204)
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type')
    handler.end_headers()
