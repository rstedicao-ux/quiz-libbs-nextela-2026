import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4
from fastapi.testclient import TestClient
import main
from reset_db import reset_database


class QuizTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        main.DB_PATH = Path(self.temp.name) / 'quiz.sqlite3'
        self.client = TestClient(main.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def user(self):
        uid = str(uuid4())
        response = self.client.post('/api/usuarios', json={'usuario_id': uid})
        self.assertEqual(response.status_code, 200)
        return uid

    def answer(self, uid, number=1, answer='mito'):
        response = self.client.post(f'/api/perguntas/{number}/respostas',
                                    json={'usuario_id': uid, 'resposta': answer})
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_two_users_all_correct_and_restart(self):
        for _ in range(2):
            uid = self.user()
            for number, answer in main.GABARITO.items():
                result = self.answer(uid, number, answer)
                self.assertEqual(result['percentual'], 100)
            self.assertEqual(result['acertos'], 6)
            self.assertEqual(result['percentil'], 100)
        main.initialize()
        data = self.client.get('/api/estatisticas').json()
        self.assertEqual(data['numero_usuarios'], 2)
        for number in main.GABARITO:
            self.assertEqual(data[f'pergunta_{number}_acertos'], 2)

    def test_fifty_users_five_correct(self):
        users = [self.user() for _ in range(50)]
        for i, uid in enumerate(users):
            result = self.answer(uid, answer='mito' if i < 5 else 'verdade')
        self.assertEqual(result['percentual'], 10)
        result = self.answer(users[5], answer='verdade')
        self.assertEqual(result['percentual'], 10)
        self.assertEqual(result['acertos'], 0)

    def test_retries_and_invalid_requests(self):
        uid = self.user()
        self.client.post('/api/usuarios', json={'usuario_id': uid})
        self.answer(uid)
        result = self.answer(uid, answer='verdade')
        self.assertTrue(result['correta'])
        self.assertEqual(result['pergunta_1_acertos'], 1)
        self.assertEqual(result['numero_usuarios'], 0)
        for number, answer, user, code in [(7, 'mito', uid, 422), (1, 'invalid', uid, 422), (1, 'mito', str(uuid4()), 404)]:
            r = self.client.post(f'/api/perguntas/{number}/respostas', json={'usuario_id': user, 'resposta': answer})
            self.assertEqual(r.status_code, code)

    def test_reset_clears_all_data_and_allows_new_quiz(self):
        uid = self.user()
        for number, answer in main.GABARITO.items():
            result = self.answer(uid, number, answer)
        self.assertEqual(result['usuarios_com_6_acertos'], 1)
        # Simulate a database that still uses the previous names.
        with main.database() as db:
            for score in range(7):
                db.execute('UPDATE contadores SET nome = ? WHERE nome = ?',
                           (f'respostas_{score}_acertos', f'usuarios_com_{score}_acertos'))
        reset_database()
        data = self.client.get('/api/estatisticas').json()
        self.assertEqual(len(data), 14)
        self.assertTrue(all(value == 0 for value in data.values()))
        for score in range(7):
            self.assertEqual(data[f'usuarios_com_{score}_acertos'], 0)
            self.assertNotIn(f'respostas_{score}_acertos', data)
        with main.database() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM respostas').fetchone()[0], 0)
        reset_database()
        result = self.answer(self.user())
        self.assertEqual(result['numero_usuarios'], 0)
        self.assertEqual(result['percentual'], 100)

    def test_exact_score_percentage_and_no_double_count(self):
        users = [self.user() for _ in range(10)]
        for uid in users[:2]:
            for number, answer in main.GABARITO.items():
                result = self.answer(uid, number, answer)
        self.assertEqual(result['usuarios_com_6_acertos'], 2)
        self.assertEqual(result['percentil'], 100)
        result = self.answer(users[1], 6, 'verdade')
        self.assertEqual(result['usuarios_com_6_acertos'], 2)
        self.assertEqual(result['percentil'], 100)
        for number, answer in main.GABARITO.items():
            result = self.answer(users[2], number, 'verdade' if answer == 'mito' else 'mito')
        self.assertEqual(result['usuarios_com_0_acertos'], 1)
        self.assertEqual(result['percentil'], 33.33)
        for number, answer in main.GABARITO.items():
            result = self.answer(users[3], number, answer if number != 6 else 'mito')
        self.assertEqual(result['usuarios_com_5_acertos'], 1)
        self.assertEqual(result['percentil'], 25)
        for number, answer in main.GABARITO.items():
            result = self.answer(users[4], number, answer if number <= 4 else ('verdade' if answer == 'mito' else 'mito'))
        self.assertEqual(result['usuarios_com_4_acertos'], 1)
        self.assertEqual(result['percentil'], 20)
        result = self.answer(users[0], 6, 'verdade')
        self.assertEqual(result['percentil'], 40)
        # Recreate missing counters as during migration of an existing database.
        with main.database() as db:
            db.execute("DELETE FROM contadores WHERE nome LIKE 'usuarios_com_%_acertos'")
        main.initialize()
        main.initialize()
        data = self.client.get('/api/estatisticas').json()
        self.assertEqual(data['usuarios_com_6_acertos'], 2)
        self.assertEqual(data['usuarios_com_5_acertos'], 1)
        self.assertEqual(data['usuarios_com_0_acertos'], 1)
        self.assertEqual(data['usuarios_com_4_acertos'], 1)
        self.assertEqual(sum(data[f'usuarios_com_{i}_acertos'] for i in range(7)), 5)

    def test_database_view_lists_all_data_without_mutation(self):
        empty = self.client.get('/api/banco')
        self.assertEqual(empty.status_code, 200)
        tables = {table['nome']: table for table in empty.json()['tabelas']}
        self.assertEqual(set(tables), {'contadores', 'usuarios', 'respostas'})
        self.assertEqual(tables['usuarios']['registros'], [])
        uid = self.user()
        self.answer(uid)
        before = self.client.get('/api/estatisticas').json()
        response = self.client.get('/api/banco')
        tables = {table['nome']: table for table in response.json()['tabelas']}
        self.assertEqual(tables['usuarios']['registros'], [{'id': uid}])
        self.assertEqual(tables['respostas']['registros'], [{'usuario_id': uid, 'pergunta': 1, 'correta': 1}])
        self.assertEqual(tables['respostas']['colunas'], ['usuario_id', 'pergunta', 'correta'])
        self.assertEqual(len(tables['contadores']['registros']), 14)
        self.assertEqual(self.client.get('/api/estatisticas').json(), before)

    def test_rename_legacy_counters_preserves_values(self):
        for pattern in ('acertou_{}', 'respostas_{}_acertos'):
            with self.subTest(pattern=pattern):
                with main.database() as db:
                    for score in range(7):
                        db.execute('UPDATE contadores SET nome = ?, valor = ? WHERE nome = ?',
                                   (pattern.format(score), score + 10, f'usuarios_com_{score}_acertos'))
                main.initialize()
                main.initialize()
                data = self.client.get('/api/estatisticas').json()
                for score in range(7):
                    self.assertEqual(data[f'usuarios_com_{score}_acertos'], score + 10)
                    self.assertNotIn(f'acertou_{score}', data)
                    self.assertNotIn(f'respostas_{score}_acertos', data)
                self.assertEqual(len(data), 14)

    def test_count_only_after_completion_and_migrate_old_total(self):
        uid = self.user()
        self.user()
        self.assertEqual(self.client.get('/api/estatisticas').json()['numero_usuarios'], 0)
        for number in range(1, 6):
            result = self.answer(uid, number, main.GABARITO[number])
            self.assertEqual(result['numero_usuarios'], 0)
        result = self.answer(uid, 6, 'verdade')
        self.assertEqual(result['numero_usuarios'], 1)
        self.assertEqual(result['usuarios_com_6_acertos'], 1)
        result = self.answer(uid, 6, 'verdade')
        self.assertEqual(result['numero_usuarios'], 1)
        with main.database() as db:
            db.execute("UPDATE contadores SET valor = 7 WHERE nome = 'numero_usuarios'")
        main.initialize()
        self.assertEqual(self.client.get('/api/estatisticas').json()['numero_usuarios'], 1)

    def test_concurrent_increments(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            users = list(pool.map(lambda _: self.user(), range(20)))
            def complete(uid):
                for number, answer in main.GABARITO.items():
                    self.answer(uid, number, answer)
                self.answer(uid, 6, 'verdade')
            list(pool.map(complete, users))
        data = self.client.get('/api/estatisticas').json()
        self.assertEqual(data['numero_usuarios'], 20)
        self.assertEqual(data['pergunta_1_acertos'], 20)


if __name__ == '__main__':
    unittest.main()
