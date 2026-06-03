from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QLineEdit, QFormLayout,
                             QComboBox, QGroupBox, QProgressDialog)
from PyQt5.QtCore import Qt, QDate, QTimer
from client.api_client import APIClient

class BuoniWidget(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- PANNELLO SINISTRO ---
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)

        # 1. Box Acquisto
        box_acquista = QGroupBox("Acquista Buono Regalo")
        box_acquista.setStyleSheet("""
            QGroupBox { font-weight: bold; border: 1px solid #CCC; border-radius: 8px; margin-top: 15px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #8C1515; }
        """)
        form_acquista = QFormLayout(box_acquista)
        form_acquista.setSpacing(15)
        form_acquista.setContentsMargins(15, 25, 15, 15)

        self.combo_valore = QComboBox()
        self.combo_valore.addItems(["20.00", "50.00", "100.00"])
        self.combo_valore.setStyleSheet("padding: 5px;")
        form_acquista.addRow("Seleziona Valore (€):", self.combo_valore)

        btn_acquista = QPushButton("Procedi al Pagamento")
        btn_acquista.setStyleSheet("background-color: #8C1515; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        btn_acquista.clicked.connect(self.simula_pagamento)
        form_acquista.addRow(btn_acquista)
        left_layout.addWidget(box_acquista)

        # 2. Box Riscatto
        box_riscatta = QGroupBox("Riscatta Codice")
        box_riscatta.setStyleSheet(box_acquista.styleSheet())
        form_riscatta = QVBoxLayout(box_riscatta)
        form_riscatta.setSpacing(10)
        form_riscatta.setContentsMargins(15, 25, 15, 15)

        self.input_codice = QLineEdit()
        self.input_codice.setPlaceholderText("Es: GIFT-1A2B3C")
        self.input_codice.setStyleSheet("padding: 5px; border: 1px dashed gray;")
        form_riscatta.addWidget(self.input_codice)

        btn_riscatta = QPushButton("Riscatta Buono")
        btn_riscatta.setStyleSheet("background-color: #E6D2B5; font-weight: bold; padding: 10px; border-radius: 5px; color: gray;")
        btn_riscatta.clicked.connect(self.riscatta_buono)
        form_riscatta.addWidget(btn_riscatta)
        left_layout.addWidget(box_riscatta)

        left_layout.addStretch()

        # --- PANNELLO DESTRO (Storico) ---
        right_panel = QGroupBox("Il tuo Portafoglio Buoni")
        right_panel.setStyleSheet(box_acquista.styleSheet())
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 25, 15, 15)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Codice", "Valore (€)", "Scadenza", "Ruolo", "Stato"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # type: ignore
        self.table.setSelectionBehavior(QTableWidget.SelectRows) # type: ignore
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # type: ignore
        right_layout.addWidget(self.table)

        btn_aggiorna = QPushButton("Aggiorna Storico")
        btn_aggiorna.clicked.connect(self.load_data)
        right_layout.addWidget(btn_aggiorna)

        main_layout.addLayout(left_layout, 1)
        main_layout.addWidget(right_panel, 2)

    def load_data(self):
        self.table.setRowCount(0)
        try:
            buoni = APIClient.get_buoni(self.user_data.get("id"))
            for b in buoni:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                self.table.setItem(row, 0, QTableWidgetItem(b.get("codice_univoco", "")))
                self.table.setItem(row, 1, QTableWidgetItem(f"€ {float(b.get('valore', 0)):.2f}"))
                self.table.setItem(row, 2, QTableWidgetItem(str(b.get("data_scadenza", ""))))
                
                # Calcola il ruolo: Acquirente o Beneficiario
                ruolo = "Acquistato da te"
                if str(b.get("beneficiario_id", "")) == str(self.user_data.get("id")):
                    ruolo = "Riscattato da te"
                self.table.setItem(row, 3, QTableWidgetItem(ruolo))

                stato = str(b.get("stato", ""))
                item_stato = QTableWidgetItem(stato)
                if stato == "ATTIVO": item_stato.setForeground(Qt.darkGreen) # type: ignore
                elif stato == "RISCATTATO": item_stato.setForeground(Qt.darkBlue) # type: ignore
                elif stato == "SCADUTO": item_stato.setForeground(Qt.darkRed) # type: ignore
                self.table.setItem(row, 4, item_stato)
                
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile caricare i buoni:\n{e}")

    def simula_pagamento(self):
        valore = float(self.combo_valore.currentText())
        
        # Simulazione del processo di pagamento tramite un dialog visivo
        dialog = QProgressDialog("Connessione al gateway di pagamento...", "Annulla", 0, 100, self)
        dialog.setWindowTitle("Pagamento Sicuro")
        dialog.setWindowModality(Qt.WindowModal) # type: ignore
        dialog.setMinimumDuration(0)
        
        # Una chiusura personalizzata tramite QTimer
        self.progress_val = 0
        def update_progress():
            self.progress_val += 20
            dialog.setValue(self.progress_val)
            if self.progress_val >= 100:
                self.timer.stop()
                if not dialog.wasCanceled():
                    self.esegui_acquisto(valore)

        self.timer = QTimer(self)
        self.timer.timeout.connect(update_progress)
        self.timer.start(300) # 300ms per 5 tick = 1.5 secondi di finto caricamento

    def esegui_acquisto(self, valore):
        # Scadenza impostata a 1 anno da oggi
        scadenza = QDate.currentDate().addYears(1).toString("yyyy-MM-dd")
        try:
            buono = APIClient.acquista_buono(self.user_data.get("id"), valore, scadenza)
            QMessageBox.information(self, "Pagamento Accettato", 
                f"Transazione completata con successo!\n\nCodice Buono: {buono.get('codice_univoco')}\n\nPuoi copiare questo codice e regalarlo a un amico!")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Acquisto fallito:\n{str(e)}")

    def riscatta_buono(self):
        codice = self.input_codice.text().strip()
        if not codice:
            QMessageBox.warning(self, "Attenzione", "Inserisci un codice valido.")
            return

        try:
            APIClient.riscatta_buono(codice, self.user_data.get("id"))
            QMessageBox.information(self, "Successo", "Buono riscattato con successo! Il valore è stato aggiunto al tuo profilo.")
            self.input_codice.clear()
            self.load_data()
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile riscattare:\n{str(e)}")
