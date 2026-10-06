import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = Path(os.getenv('DATABASE_PATH', str(Path(__file__).resolve().parents[1] / 'db' / 'quiz.sqlite3')))
GABARITO = {1: 'mito', 2: 'verdade', 3: 'mito', 4: 'mito', 5: 'mito', 6: 'verdade'}


@contextmanager
def database():
    connection = sqlite3.connect(DB_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with database() as db:
        db.execute('PRAGMA journal_mode = WAL')
        db.executescript('''
            CREATE TABLE IF NOT EXISTS contadores (nome TEXT PRIMARY KEY, valor INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS usuarios (id TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS respostas (
                usuario_id TEXT NOT NULL REFERENCES usuarios(id),
                pergunta INTEGER NOT NULL CHECK(pergunta BETWEEN 1 AND 6),
                correta INTEGER NOT NULL CHECK(correta IN (0, 1)),
                PRIMARY KEY (usuario_id, pergunta)
            );
        ''')
        db.execute('BEGIN IMMEDIATE')
        db.executemany('INSERT OR IGNORE INTO contadores(nome) VALUES (?)',
                       [(name,) for name in ['numero_usuarios', *[f'pergunta_{i}_acertos' for i in GABARITO]]])
        # Seed new counters from completed quizzes already stored in the database.
        for score in range(7):
            novo = f'usuarios_com_{score}_acertos'
            for antigo in (f'respostas_{score}_acertos', f'acertou_{score}'):
                db.execute('INSERT OR IGNORE INTO contadores(nome, valor) SELECT ?, valor FROM contadores WHERE nome = ?',
                           (novo, antigo))
                db.execute('DELETE FROM contadores WHERE nome = ?', (antigo,))
            db.execute('''
                INSERT OR IGNORE INTO contadores(nome, valor)
                SELECT ?, COUNT(*) FROM (
                    SELECT usuario_id FROM respostas GROUP BY usuario_id
                    HAVING COUNT(*) = 6 AND SUM(correta) = ?
                )
            ''', (f'usuarios_com_{score}_acertos', score))
        db.execute("UPDATE contadores SET valor = (SELECT SUM(valor) FROM contadores WHERE nome GLOB 'usuarios_com_[0-6]_acertos') WHERE nome = 'numero_usuarios'")


@asynccontextmanager
async def lifespan(app):
    initialize()
    yield


app = FastAPI(title='Quiz Nextela', lifespan=lifespan)


class Usuario(BaseModel):
    usuario_id: UUID


class Resposta(Usuario):
    resposta: str


@app.get('/api/health')
def health():
    with database() as db:
        db.execute('SELECT valor FROM contadores LIMIT 1').fetchone()
    return {'status': 'ok'}


@app.get('/api/estatisticas')
def estatisticas():
    with database() as db:
        return dict(db.execute('SELECT nome, valor FROM contadores').fetchall())


@app.get('/api/banco')
def consultar_banco():
    with database() as db:
        db.execute('PRAGMA query_only = ON')
        db.execute('BEGIN')
        tabelas = []
        nomes = db.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name").fetchall()
        for row in nomes:
            nome = row['name']
            identificador = '"' + nome.replace('"', '""') + '"'
            cursor = db.execute(f'SELECT * FROM {identificador}')
            tabelas.append({'nome': nome,
                            'colunas': [column[0] for column in cursor.description],
                            'registros': [dict(record) for record in cursor.fetchall()]})
    return {'tabelas': tabelas}


@app.post('/api/usuarios')
def registrar_usuario(usuario: Usuario):
    with database() as db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('INSERT OR IGNORE INTO usuarios VALUES (?)', (str(usuario.usuario_id),))
        total = db.execute("SELECT valor FROM contadores WHERE nome = 'numero_usuarios'").fetchone()[0]
    return {'usuario_id': str(usuario.usuario_id), 'numero_usuarios': total}


@app.post('/api/perguntas/{numero}/respostas')
def registrar_resposta(numero: int, resposta: Resposta):
    if numero not in GABARITO or resposta.resposta not in ('mito', 'verdade'):
        raise HTTPException(422, 'Pergunta ou resposta inválida')
    usuario_id = str(resposta.usuario_id)
    with database() as db:
        db.execute('BEGIN IMMEDIATE')
        if not db.execute('SELECT 1 FROM usuarios WHERE id = ?', (usuario_id,)).fetchone():
            raise HTTPException(404, 'Participação não encontrada')
        correta = int(resposta.resposta == GABARITO[numero])
        inserted = db.execute('INSERT OR IGNORE INTO respostas VALUES (?, ?, ?)',
                              (usuario_id, numero, correta)).rowcount
        if inserted and correta:
            db.execute('UPDATE contadores SET valor = valor + 1 WHERE nome = ?', (f'pergunta_{numero}_acertos',))
        correta = bool(db.execute('SELECT correta FROM respostas WHERE usuario_id = ? AND pergunta = ?',
                                  (usuario_id, numero)).fetchone()[0])
        acertos, quantidade = db.execute(
            'SELECT SUM(correta), COUNT(*) FROM respostas WHERE usuario_id = ?',
            (usuario_id,)
        ).fetchone()
        if inserted and quantidade == 6:
            db.execute('UPDATE contadores SET valor = valor + 1 WHERE nome = ?',
                       (f'usuarios_com_{acertos}_acertos',))
            db.execute("UPDATE contadores SET valor = valor + 1 WHERE nome = 'numero_usuarios'")
        contadores = dict(db.execute('SELECT nome, valor FROM contadores').fetchall())
        respondentes = db.execute('SELECT COUNT(*) FROM respostas WHERE pergunta = ?', (numero,)).fetchone()[0]
        percentil = (round(100 * contadores[f'usuarios_com_{acertos}_acertos'] / contadores['numero_usuarios'], 2)
                     if quantidade == 6 else None)
    return {'correta': correta, 'acertos': acertos,
            'percentual': round(100 * contadores[f'pergunta_{numero}_acertos'] / respondentes),
            'percentil': percentil, **contadores}
