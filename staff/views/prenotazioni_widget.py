from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt
from staff.api_client import StaffAPIClient

COLORI_STATO_PRENOTAZIONE = {
    "CONFERMATA": "#4CAF50",
    "RICHIESTA": "#FF9800",
    "IN_CORSO": "#2196F3",
    "DISDETTA": "#9E9E9E",
    "ANNULLATA": "#9E9E9E",
}


class PrenotazioniWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.prenotazioni_data = []
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        top_layout = QHBoxLayout()
        titolo = QLabel("Gestione Prenotazioni")
        titolo.setStyleSheet("font-size: 14px; font-weight: bold; color: #555;")
        top_layout.addWidget(titolo)
        top_layout.addStretch()

        btn_refresh = QPushButton("Aggiorna")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #8C1515; color: white;
                border-radius: 10px; padding: 6px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #A31F1F; }
        """)
        btn_refresh.clicked.connect(self.load_data)
        top_layout.addWidget(btn_refresh)
        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Data", "Ora", "Persone", "Tavolo", "Stato", "Note"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        self.btn_conferma = QPushButton("Conferma Prenotazione")
        self.btn_conferma.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white;
                border-radius: 10px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #66BB6A; }
        """)
        self.btn_conferma.clicked.connect(self.conferma_selezionata)

        self.btn_annulla = QPushButton("Annulla Prenotazione")
        self.btn_annulla.setStyleSheet("""
            QPushButton {
                background-color: #F44336; color: white;
                border-radius: 10px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #EF5350; }
        """)
        self.btn_annulla.clicked.connect(self.annulla_selezionata)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_conferma)
        btn_layout.addWidget(self.btn_annulla)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        try:
            self.prenotazioni_data = StaffAPIClient.get_prenotazioni()
            self.table.setRowCount(len(self.prenotazioni_data))
            for row, p in enumerate(self.prenotazioni_data):
                stato = p.get("stato", "")
                self.table.setItem(row, 0, QTableWidgetItem(str(p.get("id", ""))))
                self.table.setItem(row, 1, QTableWidgetItem(p.get("data", "")))
                self.table.setItem(row, 2, QTableWidgetItem(p.get("ora", "")))
                self.table.setItem(row, 3, QTableWidgetItem(str(p.get("numero_persone", ""))))
                self.table.setItem(row, 4, QTableWidgetItem(str(p.get("id_tavolo", "-"))))
                item_stato = QTableWidgetItem(stato)
                colore_hex = COLORI_STATO_PRENOTAZIONE.get(stato, "#000000")
                from PyQt5.QtGui import QColor
                item_stato.setForeground(QColor(colore_hex))
                self.table.setItem(row, 5, item_stato)
                note = p.get("note", "")
                allergeni = p.get("allergeni", "")
                info = f"{note} | Allergeni: {allergeni}" if allergeni else note
                self.table.setItem(row, 6, QTableWidgetItem(info))
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile caricare le prenotazioni:\n{e}")

    def conferma_selezionata(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona una prenotazione dalla tabella.")
            return

        prenotazione = self.prenotazioni_data[row]
        if prenotazione.get("stato") != "RICHIESTA":
            QMessageBox.information(self, "Info", "Solo le prenotazioni in stato RICHIESTA possono essere confermate.")
            return

        tavolo_id, ok = QInputDialog.getText(
            self, "Assegna Tavolo",
            f"Prenotazione per {prenotazione.get('numero_persone')} persone.\nInserisci il numero del tavolo:"
        )

        if ok and tavolo_id.strip():
            try:
                success = StaffAPIClient.conferma_prenotazione(prenotazione.get("id"), tavolo_id.strip())
                if success:
                    QMessageBox.information(self, "Successo", f"Prenotazione confermata al tavolo {tavolo_id}.")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile confermare la prenotazione.")
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def annulla_selezionata(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona una prenotazione dalla tabella.")
            return

        prenotazione = self.prenotazioni_data[row]
        risposta = QMessageBox.question(
            self, "Conferma Annullamento",
            f"Annullare la prenotazione #{prenotazione.get('id')}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if risposta == QMessageBox.Yes:
            try:
                success = StaffAPIClient.annulla_prenotazione(prenotazione.get("id"))
                if success:
                    QMessageBox.information(self, "Successo", "Prenotazione annullata.")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile annullare la prenotazione.")
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))
