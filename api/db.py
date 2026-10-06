import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for p in [current_dir, parent_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except Exception:
    PSYCOPG2_AVAILABLE = False

GABARITO = {1: 'mito', 2: 'verdade', 3: 'mito', 4: 'mito', 5: 'mito', 6: 'verdade'}


def get_postgres_url():
    for key in ['POSTGRES_URL', 'POSTGRES_URL_NON_POOLING', 'DATABASE_URL', 'POSTGRES_PRISMA_URL']:
        val = os.environ.get(key)
        if val:
            return val
    return None


def get_db():
    url = get_postgres_url()
    if not url or not PSYCOPG2_AVAILABLE:
        return None
    try:
        conn = psycopg2.connect(url, connect_timeout=5)
        conn.autocommit = False
        return conn
    except Exception as e:
        print(f"Error connecting to Postgres: {e}")
        return None


def init_db():
    conn = get_db()
    if not conn:
        return False
    try:
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
        return True
    except Exception as e:
        print(f"Error init_db: {e}")
        try:
            conn.close()
        except Exception:
            pass
        return False


def json_response(handler, status, body):
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
