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
        
        from PyQt5.QtWidgets import QDateEdit, QCheckBox
        from PyQt5.QtCore import QDate
        
        self.chk_tutte = QCheckBox("Mostra tutte")
        self.chk_tutte.stateChanged.connect(self.load_data)
        top_layout.addWidget(self.chk_tutte)
        
        top_layout.addWidget(QLabel("Filtra per Data:"))
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.dateChanged.connect(self.load_data)
        top_layout.addWidget(self.date_picker)
        
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
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Cliente", "Data", "Ora", "Persone", "Tavolo", "Stato", "Note"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents) # type: ignore
        header.setSectionResizeMode(7, QHeaderView.Stretch) # type: ignore
        self.table.setSelectionBehavior(QTableWidget.SelectRows) # type: ignore
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # type: ignore
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

        # Pannello Overbooking
        self.panel_overbooking = QWidget()
        self.panel_overbooking.setStyleSheet("background-color: #f8f9fa; border-top: 2px solid #ccc; padding: 10px;")
        ob_layout = QVBoxLayout()
        self.lbl_overbooking = QLabel()
        self.lbl_overbooking.setStyleSheet("color: #d32f2f; font-weight: bold; font-size: 13px;")
        ob_layout.addWidget(self.lbl_overbooking)
        
        ob_btns = QHBoxLayout()
        ob_btns.addStretch()
        
        btn_assegna = QPushButton("ASSEGNA TAVOLO")
        btn_assegna.setStyleSheet("background-color: #9E9E9E; color: white; padding: 8px 16px; border-radius: 15px; font-weight: bold;")
        btn_assegna.clicked.connect(self.assegna_tavolo_manuale)
        
        btn_disdici = QPushButton("DISDICI")
        btn_disdici.setStyleSheet("background-color: #9E9E9E; color: white; padding: 8px 16px; border-radius: 15px; font-weight: bold;")
        btn_disdici.clicked.connect(self.annulla_selezionata)
        
        btn_sposta = QPushButton("SPOSTA DI DATA")
        btn_sposta.setStyleSheet("background-color: #9E9E9E; color: white; padding: 8px 16px; border-radius: 15px; font-weight: bold;")
        btn_sposta.clicked.connect(self.sposta_data)
        
        ob_btns.addWidget(btn_assegna)
        ob_btns.addWidget(btn_disdici)
        ob_btns.addWidget(btn_sposta)
        ob_btns.addStretch()
        ob_layout.addLayout(ob_btns)
        
        self.panel_overbooking.setLayout(ob_layout)
        self.panel_overbooking.hide()
        
        layout.addWidget(self.panel_overbooking)

        self.setLayout(layout)

    def load_data(self):
        self.date_picker.setEnabled(not self.chk_tutte.isChecked())
        try:
            if self.chk_tutte.isChecked():
                self.prenotazioni_data = StaffAPIClient.get_prenotazioni()
            else:
                data_str = self.date_picker.date().toString("yyyy-MM-dd")
                self.prenotazioni_data = StaffAPIClient.get_prenotazioni(data_str)
                
            def _create_centered_item(text):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignCenter) # type: ignore
                return item

            self.table.setRowCount(len(self.prenotazioni_data))
            for row, p in enumerate(self.prenotazioni_data):
                stato = p.get("stato", "")
                self.table.setItem(row, 0, _create_centered_item(p.get("id", "")))
                self.table.setItem(row, 1, _create_centered_item(p.get("nome_cliente", "")))
                self.table.setItem(row, 2, _create_centered_item(p.get("data", "")))
                self.table.setItem(row, 3, _create_centered_item(p.get("ora", "")))
                self.table.setItem(row, 4, _create_centered_item(p.get("numero_persone", "")))
                self.table.setItem(row, 5, _create_centered_item(p.get("tavolo_id", "-")))
                
                item_stato = _create_centered_item(stato)
                colore_hex = COLORI_STATO_PRENOTAZIONE.get(stato, "#000000")
                from PyQt5.QtGui import QColor
                item_stato.setForeground(QColor(colore_hex))
                self.table.setItem(row, 6, item_stato)
                
                note = p.get("note", "")
                allergeni = p.get("allergeni", "")
                info = f"{note} | Allergeni: {allergeni}" if allergeni else note
                self.table.setItem(row, 7, QTableWidgetItem(str(info)))
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

        try:
            success, result = StaffAPIClient.auto_conferma_prenotazione(prenotazione.get("id"))
            if success:
                self.panel_overbooking.hide()
                QMessageBox.information(self, "Successo", f"Prenotazione confermata automaticamente al tavolo {result}.")
                self.load_data()
            elif result == "OVERBOOKING":
                nome = prenotazione.get("nome_ospite") or f"Cliente ID {prenotazione.get('cliente_id')}"
                self.lbl_overbooking.setText(f"> [WARNING] OVERBOOKING RILEVATO!\nLa richiesta di {nome} non ha tavoli compatibili liberi.")
                self.panel_overbooking.show()
            else:
                QMessageBox.warning(self, "Errore", "Impossibile confermare la prenotazione.")
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e))

    def assegna_tavolo_manuale(self):
        row = self.table.currentRow()
        if row < 0: return
        prenotazione = self.prenotazioni_data[row]
        
        tavolo_id, ok = QInputDialog.getText(
            self, "Assegna Tavolo",
            f"Prenotazione per {prenotazione.get('numero_persone')} persone.\nInserisci il numero del tavolo:"
        )

        if ok and tavolo_id.strip():
            try:
                success = StaffAPIClient.conferma_prenotazione(prenotazione.get("id"), tavolo_id.strip())
                if success:
                    self.panel_overbooking.hide()
                    QMessageBox.information(self, "Successo", f"Prenotazione confermata al tavolo {tavolo_id}.")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile confermare la prenotazione.")
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def sposta_data(self):
        row = self.table.currentRow()
        if row < 0: return
        prenotazione = self.prenotazioni_data[row]
        
        from PyQt5.QtWidgets import QDateEdit, QDialog, QDialogButtonBox
        from PyQt5.QtCore import QDate
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Sposta di Data")
        l = QVBoxLayout(dialog)
        l.addWidget(QLabel("Scegli la nuova data:"))
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        # Parse existing date or default to current
        old_date_str = prenotazione.get("data", "")
        if old_date_str:
            d = QDate.fromString(old_date_str, "yyyy-MM-dd")
            if d.isValid():
                date_edit.setDate(d)
            else:
                date_edit.setDate(QDate.currentDate())
        else:
            date_edit.setDate(QDate.currentDate())
        l.addWidget(date_edit)
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel) # type: ignore
        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)
        l.addWidget(btns)
        
        if dialog.exec_() == QDialog.Accepted:
            nuova_data = date_edit.date().toString("yyyy-MM-dd")
            try:
                success = StaffAPIClient.modifica_prenotazione(prenotazione.get("id"), {"data": nuova_data})
                if success:
                    self.panel_overbooking.hide()
                    QMessageBox.information(self, "Successo", f"Prenotazione spostata al {nuova_data}. Rimane in attesa.")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile spostare la prenotazione.")
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
            QMessageBox.Yes | QMessageBox.No # type: ignore
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
