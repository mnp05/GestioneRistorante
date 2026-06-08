import sys
import os
import unittest
import tempfile
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import server.models.base_repository as base_repo
from server.app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        # Mock DATA_DIR
        self.tmpdir = tempfile.TemporaryDirectory()
        self.orig_data_dir = base_repo.DATA_DIR
        base_repo.DATA_DIR = Path(self.tmpdir.name)
        
        # Setup Flask Test Client
        app.config['TESTING'] = True
        self.client = app.test_client()
        
    def tearDown(self):
        base_repo.DATA_DIR = self.orig_data_dir
        self.tmpdir.cleanup()

    def test_get_menu(self):
        # Anche con un DB vuoto, l'endpoint /api/menu deve rispondere 200 OK con una lista vuota
        response = self.client.get('/api/menu')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn("data", data)
        self.assertIsInstance(data["data"], list)

    def test_get_tables(self):
        # Test endpoint tavoli
        response = self.client.get('/api/tables')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn("data", data)
        self.assertIsInstance(data["data"], list)

if __name__ == "__main__":
    unittest.main()
