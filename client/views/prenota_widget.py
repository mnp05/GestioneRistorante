from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDateEdit, QTimeEdit, QSpinBox, 
                             QLineEdit, QMessageBox, QFormLayout, QGroupBox, QDialog, QDialogButtonBox)
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
        self.input_data.setMinimumDate(QDate.currentDate().addDays(-1))
        self.input_data.setSpecialValueText("Seleziona Data")
        self.input_data.setDate(QDate.currentDate().addDays(-1))
        self.input_data.setStyleSheet("padding: 5px;")

        self.input_ora = QTimeEdit()
        self.input_ora.setTime(QTime(20, 0))
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

        self.label_disponibilita = QLabel("Posti disponibili: Seleziona Data e Ora")
        self.label_disponibilita.setStyleSheet("font-weight: bold; color: #8C1515; font-size: 14px;")

        self.btn_prenota = QPushButton("Conferma Prenotazione")
        self.btn_prenota.setEnabled(False)
        self.btn_prenota.setStyleSheet("""
            QPushButton {
                background-color: #8C1515;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #A31F1F; }
            QPushButton:disabled { background-color: #CCCCCC; color: #666666; }
        """)
        self.btn_prenota.clicked.connect(self.effettua_prenotazione)

        form_layout.addRow("Data:", self.input_data)
        form_layout.addRow("Ora:", self.input_ora)
        form_layout.addRow("Persone:", self.input_persone)
        form_layout.addRow("Allergeni:", self.input_allergeni)
        form_layout.addRow("Note:", self.input_note)
        form_layout.addRow(self.label_disponibilita)
        form_layout.addRow(self.btn_prenota)

        self.input_data.dateChanged.connect(self.aggiorna_disponibilita)
        self.input_ora.timeChanged.connect(self.aggiorna_disponibilita)
        self.input_persone.valueChanged.connect(self.aggiorna_disponibilita)
        
        self.aggiorna_disponibilita()

        # --- DESTRA: Storico Prenotazioni ---
        right_panel = QGroupBox("Le Mie Prenotazioni")
        right_panel.setStyleSheet(left_panel.styleSheet())
        right_layout = QVBoxLayout(right_panel)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Data", "Ora", "Persone", "Stato", "Tavolo"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        self.table.setSelectionBehavior(QTableWidget.SelectRows) 
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) 
        right_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_aggiorna = QPushButton("Aggiorna")
        btn_modifica = QPushButton("Modifica")
        btn_annulla = QPushButton("Annulla Prenotazione")
        
        btn_aggiorna.clicked.connect(self.load_data)
        btn_modifica.clicked.connect(self.modifica_prenotazione)
        btn_annulla.clicked.connect(self.annulla_prenotazione)

        btn_layout.addWidget(btn_aggiorna)
        btn_layout.addWidget(btn_modifica)
        btn_layout.addWidget(btn_annulla)
        right_layout.addLayout(btn_layout)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

    def aggiorna_disponibilita(self):
        data_selezionata = self.input_data.date()
        ora_selezionata = self.input_ora.time()
        
        if data_selezionata == self.input_data.minimumDate():
            self.label_disponibilita.setText("Posti disponibili: Seleziona Data")
            self.label_disponibilita.setStyleSheet("font-weight: bold; color: #8C1515; font-size: 14px;")
            self.btn_prenota.setEnabled(False)
            return

        data_str = data_selezionata.toString("yyyy-MM-dd")
        ora_str = ora_selezionata.toString("HH:mm")
        persone = self.input_persone.value()

        try:
            posti = APIClient.get_posti_disponibili(data_str, ora_str)
            if posti >= persone:
                self.label_disponibilita.setText(f"Posti disponibili: {posti} ✅")
                self.label_disponibilita.setStyleSheet("font-weight: bold; color: green; font-size: 14px;")
                self.btn_prenota.setEnabled(True)
            else:
                self.label_disponibilita.setText(f"Posti disponibili: {posti} ❌")
                self.label_disponibilita.setStyleSheet("font-weight: bold; color: red; font-size: 14px;")
                self.btn_prenota.setEnabled(False)
        except Exception:
            self.label_disponibilita.setText("Errore verifica disponibilità.")
            self.btn_prenota.setEnabled(False)

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
                if stato == "CONFERMATA": item_stato.setForeground(Qt.darkGreen) 
                elif stato == "RICHIESTA": item_stato.setForeground(Qt.darkYellow) 
                elif stato == "DISDETTA": item_stato.setForeground(Qt.darkRed) 
                self.table.setItem(row, 4, item_stato)
                
                tavolo = str(p.get("tavolo_id", ""))
                self.table.setItem(row, 5, QTableWidgetItem(tavolo if tavolo else "In Attesa"))
        except Exception as e:
            print(f"Errore caricamento prenotazioni: {e}")

    def effettua_prenotazione(self):
        dati = {
            "cliente_id": self.user_data.get("id"),
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
            
            # Resetta i campi ai valori speciali iniziali
            self.input_data.blockSignals(True)
            self.input_ora.blockSignals(True)
            self.input_data.setDate(self.input_data.minimumDate())
            self.input_ora.setTime(QTime(20, 0))
            self.input_data.blockSignals(False)
            self.input_ora.blockSignals(False)
            self.aggiorna_disponibilita()
            
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile prenotare:\n{str(e)}")

    def annulla_prenotazione(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attenzione", "Seleziona una prenotazione da annullare.")
            return

        row = selected[0].row()
        booking_id = self.table.item(row, 0).text() 
        stato = self.table.item(row, 4).text() 

        if stato in ["DISDETTA", "CONCLUSA"]:
            QMessageBox.warning(self, "Attenzione", "Questa prenotazione non può essere annullata.")
            return

        risposta = QMessageBox.question(
            self, "Conferma Annullamento",
            "Vuoi davvero annullare questa prenotazione?",
            QMessageBox.Yes | QMessageBox.No 
        )

        if risposta == QMessageBox.Yes:
            try:
                APIClient.cancella_prenotazione(booking_id)
                QMessageBox.information(self, "Successo", "Prenotazione annullata.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile annullare:\n{str(e)}")

    def modifica_prenotazione(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attenzione", "Seleziona una prenotazione da modificare.")
            return

        row = selected[0].row()
        booking_id = self.table.item(row, 0).text()
        data_str = self.table.item(row, 1).text()
        ora_str = self.table.item(row, 2).text()
        persone_str = self.table.item(row, 3).text()
        stato = self.table.item(row, 4).text()

        if stato in ["DISDETTA", "ANNULLATA", "CONCLUSA"]:
            QMessageBox.warning(self, "Attenzione", "Questa prenotazione non può essere modificata.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Modifica Prenotazione")
        layout = QFormLayout(dialog)

        input_data = QDateEdit()
        input_data.setCalendarPopup(True)
        input_data.setDate(QDate.fromString(data_str, "yyyy-MM-dd"))
        input_data.setMinimumDate(QDate.currentDate())
        
        input_ora = QTimeEdit()
        input_ora.setTime(QTime.fromString(ora_str, "HH:mm"))
        
        input_persone = QSpinBox()
        input_persone.setRange(1, 20)
        try:
            input_persone.setValue(int(persone_str))
        except ValueError:
            pass

        layout.addRow("Nuova Data:", input_data)
        layout.addRow("Nuova Ora:", input_ora)
        layout.addRow("Nuove Persone:", input_persone)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addRow(btn_box)

        if dialog.exec_() == QDialog.Accepted:
            nuovi_dati = {
                "data": input_data.date().toString("yyyy-MM-dd"),
                "ora": input_ora.time().toString("HH:mm"),
                "numero_persone": input_persone.value()
            }
            try:
                APIClient.modifica_prenotazione(booking_id, nuovi_dati)
                QMessageBox.information(self, "Successo", "Prenotazione modificata con successo!")
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, "Errore Modifica", str(e))
