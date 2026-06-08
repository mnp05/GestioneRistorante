import sys
import os
import unittest
import tempfile
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import server.models.base_repository as base_repo
from server.controllers.booking_controller import BookingController
from server.models.table import TableRepository

class TestBookingController(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.orig_data_dir = base_repo.DATA_DIR
        base_repo.DATA_DIR = Path(self.tmpdir.name)
        
        self.controller = BookingController()
        self.table_repo = TableRepository()
        
    def tearDown(self):
        base_repo.DATA_DIR = self.orig_data_dir
        self.tmpdir.cleanup()

    def test_auto_assign_success(self):
        oggi = datetime.now().strftime("%Y-%m-%d")
        
        # Creiamo un tavolo per 5 persone
        self.table_repo.create_or_update({
            "numero": "T1",
            "capienza": 5,
            "coordinata_x": 0,
            "coordinata_y": 0,
            "stato": "DISPONIBILE",
            "data": oggi
        })
        
        dati_prenotazione = {
            "cliente_id": "4",
            "nome_ospite": "",
            "data": oggi,
            "ora": "20:30",
            "numero_persone": "5",
            "allergeni": "Nessuno",
            "note": ""
        }
        
        risultato = self.controller.handle_new_booking(dati_prenotazione)
        self.assertEqual(risultato["stato"], "RICHIESTA")
        
        # Tenta assegnazione
        tavolo_assegnato = self.controller.handle_try_auto_confirm(str(risultato["id"]))
        self.assertEqual(tavolo_assegnato, "T1")
        
        prenotazione_aggiornata = self.controller.booking_repo.get_by_id(str(risultato["id"]))
        assert prenotazione_aggiornata is not None
        self.assertEqual(prenotazione_aggiornata["stato"], "CONFERMATA")
        self.assertEqual(prenotazione_aggiornata["tavolo_id"], "T1")

    def test_overbooking(self):
        oggi = datetime.now().strftime("%Y-%m-%d")
        
        dati_prenotazione = {
            "cliente_id": "4",
            "nome_ospite": "",
            "data": oggi,
            "ora": "20:30",
            "numero_persone": "5",
            "allergeni": "Nessuno",
            "note": ""
        }
        
        risultato = self.controller.handle_new_booking(dati_prenotazione)
        
        # Tenta assegnazione, ma fallirà
        tavolo_assegnato = self.controller.handle_try_auto_confirm(str(risultato["id"]))
        self.assertIsNone(tavolo_assegnato)
        
        prenotazione_aggiornata = self.controller.booking_repo.get_by_id(str(risultato["id"]))
        assert prenotazione_aggiornata is not None
        self.assertEqual(prenotazione_aggiornata["stato"], "RICHIESTA")

if __name__ == "__main__":
    unittest.main()
