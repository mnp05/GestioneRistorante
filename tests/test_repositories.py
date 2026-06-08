import sys
import os
import unittest
import tempfile
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import server.models.base_repository as base_repo
from server.models.user import UserRepository

class TestUserRepository(unittest.TestCase):
    def setUp(self):
        # Mock DATA_DIR con cartella temporanea
        self.tmpdir = tempfile.TemporaryDirectory()
        self.orig_data_dir = base_repo.DATA_DIR
        base_repo.DATA_DIR = Path(self.tmpdir.name)
        
        self.user_repo = UserRepository()

    def tearDown(self):
        # Ripristino DATA_DIR originale
        base_repo.DATA_DIR = self.orig_data_dir
        self.tmpdir.cleanup()

    def test_get_next_id_empty(self):
        # Test generazione ID su un CSV appena creato (vuoto)
        self.assertEqual(self.user_repo.get_next_id(), 1)

    def test_create_and_get_user(self):
        user_data = {
            "nome": "Mario",
            "cognome": "Rossi",
            "email": "mario@example.com",
            "password": "pwd",
            "ruolo": "cliente"
        }
        res = self.user_repo.create(user_data)
        self.assertIn("id", res)
        self.assertEqual(res["id"], 1)

        # Controllo recupero utente
        user = self.user_repo.get_by_id(str(res["id"]))
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], "mario@example.com")

    def test_authenticate(self):
        self.user_repo.create({
            "nome": "Luigi",
            "email": "luigi@example.com",
            "password": "secure"
        })
        
        # Login valido
        user = self.user_repo.authenticate("luigi@example.com", "secure")
        self.assertIsNotNone(user)
        self.assertEqual(user["nome"], "Luigi")
        
        # Login non valido (password errata)
        bad_user = self.user_repo.authenticate("luigi@example.com", "wrong")
        self.assertIsNone(bad_user)
        
    def test_duplicate_email(self):
        self.user_repo.create({"email": "test@test.com", "password": "123"})
        with self.assertRaises(ValueError):
            self.user_repo.create({"email": "test@test.com", "password": "456"})

if __name__ == "__main__":
    unittest.main()
