from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QLineEdit, QFormLayout,
                             QDialog, QDialogButtonBox, QCheckBox)
from PyQt5.QtCore import Qt
from staff.api_client import StaffAPIClient


class StaffMenuWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.piatti_data = []
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        top_layout = QHBoxLayout()
        titolo = QLabel("Gestione Menù")
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nome", "Prezzo", "Allergeni", "Categoria", "Attivo"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # type: ignore
        self.table.setSelectionBehavior(QTableWidget.SelectRows) # type: ignore
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # type: ignore
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        btn_aggiungi = QPushButton("Aggiungi Prodotto")
        btn_aggiungi.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white;
                border-radius: 10px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #66BB6A; }
        """)
        btn_aggiungi.clicked.connect(self.aggiungi_piatto)

        btn_modifica = QPushButton("Modifica Prodotto")
        btn_modifica.setStyleSheet("""
            QPushButton {
                background-color: #FF9800; color: white;
                border-radius: 10px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #FFB74D; }
        """)
        btn_modifica.clicked.connect(self.modifica_piatto)

        btn_disattiva = QPushButton("Disattiva Prodotto")
        btn_disattiva.setStyleSheet("""
            QPushButton {
                background-color: #F44336; color: white;
                border-radius: 10px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #EF5350; }
        """)
        btn_disattiva.clicked.connect(self.disattiva_piatto)
        
        btn_elimina = QPushButton("Elimina Prodotto")
        btn_elimina.setStyleSheet("""
            QPushButton {
                background-color: #8C1515; color: white;
                border-radius: 10px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #A31F1F; }
        """)
        btn_elimina.clicked.connect(self.elimina_definitivo)

        btn_attiva = QPushButton("Attiva Prodotto")
        btn_attiva.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; color: white;
                border-radius: 10px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #42A5F5; }
        """)
        btn_attiva.clicked.connect(self.attiva_piatto)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_aggiungi)
        btn_layout.addWidget(btn_modifica)
        btn_layout.addWidget(btn_disattiva)
        btn_layout.addWidget(btn_attiva)
        btn_layout.addWidget(btn_elimina)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        try:
            self.piatti_data = StaffAPIClient.get_menu()
            self.table.setRowCount(len(self.piatti_data))
            for row, p in enumerate(self.piatti_data):
                self.table.setItem(row, 0, QTableWidgetItem(str(p.get("id", ""))))
                self.table.setItem(row, 1, QTableWidgetItem(p.get("nome", "")))
                self.table.setItem(row, 2, QTableWidgetItem(f"€{p.get('prezzo', '')}"))
                self.table.setItem(row, 3, QTableWidgetItem(p.get("allergeni", "")))
                self.table.setItem(row, 4, QTableWidgetItem(str(p.get("categoria_id", ""))))
                attivo = str(p.get("attivo", "")).lower() in ("true", "1", "t")
                item_attivo = QTableWidgetItem("Sì" if attivo else "No")
                if not attivo:
                    from PyQt5.QtGui import QColor
                    item_attivo.setForeground(QColor("#F44336"))
                self.table.setItem(row, 5, item_attivo)
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile caricare il menù:\n{e}")

    def _crea_dialog_piatto(self, titolo, dati_iniziali=None):
        """Crea un dialog riutilizzabile per aggiunta/modifica piatto."""
        dialog = QDialog(self)
        dialog.setWindowTitle(titolo)
        dialog.setMinimumWidth(400)

        form = QFormLayout()
        campi = {}

        for campo, label in [("nome", "Nome:"), ("descrizione", "Descrizione:"),
                              ("prezzo", "Prezzo (€):"), ("allergeni", "Allergeni:"),
                              ("categoria_id", "Categoria ID:")]:
            input_field = QLineEdit()
            if dati_iniziali:
                input_field.setText(str(dati_iniziali.get(campo, "")))
            campi[campo] = input_field
            form.addRow(label, input_field)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel) # type: ignore
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        dialog.setLayout(form)
        return dialog, campi

    def aggiungi_piatto(self):
        dialog, campi = self._crea_dialog_piatto("Nuovo Piatto")

        if dialog.exec_() == QDialog.Accepted:
            dati = {campo: input_field.text() for campo, input_field in campi.items()}
            try:
                StaffAPIClient.aggiungi_piatto(dati)
                QMessageBox.information(self, "Successo", "Piatto aggiunto con successo.")
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def modifica_piatto(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un piatto dalla tabella.")
            return

        piatto = self.piatti_data[row]
        dialog, campi = self._crea_dialog_piatto("Modifica Piatto", piatto)

        if dialog.exec_() == QDialog.Accepted:
            dati = {campo: input_field.text() for campo, input_field in campi.items()}
            try:
                success = StaffAPIClient.modifica_piatto(piatto.get("id"), dati)
                if success:
                    QMessageBox.information(self, "Successo", "Piatto modificato con successo.")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile modificare il piatto.")
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def disattiva_piatto(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un piatto dalla tabella.")
            return

        piatto = self.piatti_data[row]
        risposta = QMessageBox.question(
            self, "Conferma Disattivazione",
            f"Disattivare il piatto '{piatto.get('nome')}'?",
            QMessageBox.Yes | QMessageBox.No # type: ignore
        )

        if risposta == QMessageBox.Yes:
            try:
                success = StaffAPIClient.disattiva_piatto(piatto.get("id"))
                if success:
                    QMessageBox.information(self, "Successo", "Piatto disattivato.")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile disattivare il piatto.")
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def elimina_definitivo(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un piatto dalla tabella.")
            return

        piatto = self.piatti_data[row]
        risposta = QMessageBox.question(
            self, "Conferma Eliminazione",
            f"Vuoi davvero eliminare fisicamente il piatto '{piatto.get('nome')}' dal database?\nAttenzione: l'operazione è irreversibile e potrebbe causare errori se il piatto è presente in ordini passati.",
            QMessageBox.Yes | QMessageBox.No # type: ignore
        )

        if risposta == QMessageBox.Yes:
            try:
                success = StaffAPIClient.rimuovi_piatto_definitivamente(piatto.get("id"))
                if success:
                    QMessageBox.information(self, "Successo", "Piatto eliminato definitivamente dal sistema.")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile eliminare il piatto.")
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def attiva_piatto(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un piatto dalla tabella.")
            return

        piatto = self.piatti_data[row]
        risposta = QMessageBox.question(
            self, "Conferma Riattivazione",
            f"Riattivare il piatto '{piatto.get('nome')}'?",
            QMessageBox.Yes | QMessageBox.No # type: ignore
        )

        if risposta == QMessageBox.Yes:
            try:
                success = StaffAPIClient.attiva_piatto(piatto.get("id"))
                if success:
                    QMessageBox.information(self, "Successo", "Piatto riattivato con successo.")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile riattivare il piatto.")
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))
