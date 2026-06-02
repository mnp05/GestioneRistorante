from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDateEdit, QTimeEdit, QSpinBox, 
                             QLineEdit, QMessageBox, QFormLayout, QGroupBox)
from PyQt5.QtCore import Qt, QDate, QTime
from client.api_client import APIClient

class PrenotaWidget(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- SINISTRA: Form Nuova Prenotazione ---
        left_panel = QGroupBox("Nuova Prenotazione")
        left_panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #CCC;
                border-radius: 8px;
                margin-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #8C1515;
            }
        """)
        form_layout = QFormLayout(left_panel)
        form_layout.setSpacing(15)

        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        self.input_data.setDate(QDate.currentDate())
        self.input_data.setMinimumDate(QDate.currentDate())
        self.input_data.setStyleSheet("padding: 5px;")

        self.input_ora = QTimeEdit()
        self.input_ora.setTime(QTime(20, 0)) # Default cena
        self.input_ora.setStyleSheet("padding: 5px;")

        self.input_persone = QSpinBox()
        self.input_persone.setRange(1, 20)
        self.input_persone.setStyleSheet("padding: 5px;")

        self.input_allergeni = QLineEdit()
        self.input_allergeni.setPlaceholderText("Es. Intolleranza al lattosio...")
        self.input_allergeni.setStyleSheet("padding: 5px;")

        self.input_note = QLineEdit()
        self.input_note.setPlaceholderText("Es. Seggiolone per bambino, tavolo vicino finestra...")
        self.input_note.setStyleSheet("padding: 5px;")

        btn_prenota = QPushButton("Conferma Prenotazione")
        btn_prenota.setStyleSheet("""
            QPushButton {
                background-color: #8C1515;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #A31F1F; }
        """)
        btn_prenota.clicked.connect(self.effettua_prenotazione)

        form_layout.addRow("Data:", self.input_data)
        form_layout.addRow("Ora:", self.input_ora)
        form_layout.addRow("Persone:", self.input_persone)
        form_layout.addRow("Allergeni:", self.input_allergeni)
        form_layout.addRow("Note:", self.input_note)
        form_layout.addRow(btn_prenota)

        # --- DESTRA: Storico Prenotazioni ---
        right_panel = QGroupBox("Le Mie Prenotazioni")
        right_panel.setStyleSheet(left_panel.styleSheet())
        right_layout = QVBoxLayout(right_panel)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Data", "Ora", "Persone", "Stato", "Tavolo"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # type: ignore
        self.table.setSelectionBehavior(QTableWidget.SelectRows) # type: ignore
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # type: ignore
        right_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_aggiorna = QPushButton("Aggiorna")
        btn_annulla = QPushButton("Annulla Prenotazione")
        
        btn_aggiorna.clicked.connect(self.load_data)
        btn_annulla.clicked.connect(self.annulla_prenotazione)

        btn_layout.addWidget(btn_aggiorna)
        btn_layout.addWidget(btn_annulla)
        right_layout.addLayout(btn_layout)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

    def load_data(self):
        self.table.setRowCount(0)
        try:
            prenotazioni = APIClient.get_prenotazioni_utente(self.user_data.get("id"))
            for p in prenotazioni:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(p.get("id", ""))))
                self.table.setItem(row, 1, QTableWidgetItem(str(p.get("data", ""))))
                self.table.setItem(row, 2, QTableWidgetItem(str(p.get("ora", ""))))
                self.table.setItem(row, 3, QTableWidgetItem(str(p.get("numero_persone", ""))))
                
                stato = str(p.get("stato", ""))
                item_stato = QTableWidgetItem(stato)
                if stato == "CONFERMATA": item_stato.setForeground(Qt.darkGreen) # type: ignore
                elif stato == "RICHIESTA": item_stato.setForeground(Qt.darkYellow) # type: ignore
                elif stato == "DISDETTA": item_stato.setForeground(Qt.darkRed) # type: ignore
                self.table.setItem(row, 4, item_stato)
                
                tavolo = str(p.get("id_tavolo", ""))
                self.table.setItem(row, 5, QTableWidgetItem(tavolo if tavolo else "In Attesa"))
        except Exception as e:
            print(f"Errore caricamento prenotazioni: {e}")

    def effettua_prenotazione(self):
        dati = {
            "id_cliente": self.user_data.get("id"),
            "data": self.input_data.date().toString("yyyy-MM-dd"),
            "ora": self.input_ora.time().toString("HH:mm"),
            "numero_persone": self.input_persone.value(),
            "allergeni": self.input_allergeni.text(),
            "note": self.input_note.text(),
            "stato": "RICHIESTA" # Il server lo cambia in CONFERMATA se trova tavolo
        }

        try:
            APIClient.effettua_prenotazione(dati)
            QMessageBox.information(self, "Successo", "Prenotazione inviata con successo!")
            self.input_allergeni.clear()
            self.input_note.clear()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile prenotare:\n{str(e)}")

    def annulla_prenotazione(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attenzione", "Seleziona una prenotazione da annullare.")
            return

        row = selected[0].row()
        booking_id = self.table.item(row, 0).text() # type: ignore
        stato = self.table.item(row, 4).text() # type: ignore

        if stato in ["DISDETTA", "CONCLUSA"]:
            QMessageBox.warning(self, "Attenzione", "Questa prenotazione non può essere annullata.")
            return

        risposta = QMessageBox.question(
            self, "Conferma Annullamento",
            "Vuoi davvero annullare questa prenotazione?",
            QMessageBox.Yes | QMessageBox.No # type: ignore
        )

        if risposta == QMessageBox.Yes:
            try:
                APIClient.cancella_prenotazione(booking_id)
                QMessageBox.information(self, "Successo", "Prenotazione annullata.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile annullare:\n{str(e)}")
