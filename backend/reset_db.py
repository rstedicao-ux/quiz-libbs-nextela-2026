"""Limpa os dados do quiz, mantendo o schema e os contadores inicializados."""
from main import database, initialize


def reset_database():
    # Migrate legacy counter names before clearing every counter.
    initialize()
    with database() as db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('DELETE FROM respostas')
        db.execute('DELETE FROM usuarios')
        # Includes numero_usuarios, pergunta_N_acertos and usuarios_com_N_acertos.
        db.execute('UPDATE contadores SET valor = 0')


if __name__ == '__main__':
    reset_database()
    print('Banco zerado. Recarregue a pagina antes de iniciar um novo quiz.')
