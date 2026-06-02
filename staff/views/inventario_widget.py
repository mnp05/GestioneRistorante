from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QLineEdit, QFormLayout,
                             QDialog, QDialogButtonBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from staff.api_client import StaffAPIClient

COLORI_STATO_INVENTARIO = {
    "SUFFICIENTE": QColor("#4CAF50"),
    "IN_ESAURIMENTO": QColor("#FF9800"),
    "ESAURITO": QColor("#F44336"),
}


class InventarioWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.inventario_data = []
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        top_layout = QHBoxLayout()
        titolo = QLabel("Gestione Inventario")
        titolo.setStyleSheet("font-size: 14px; font-weight: bold; color: #555;")
        top_layout.addWidget(titolo)
        top_layout.addStretch()

        self.lbl_alert = QLabel("")
        self.lbl_alert.setStyleSheet("color: #F44336; font-weight: bold; font-size: 13px;")
        top_layout.addWidget(self.lbl_alert)

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
            "ID", "Nome", "Quantità", "Unità", "Soglia Min.", "Categoria", "Stato"
        ])
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.Stretch)     # type: ignore
        self.table.setSelectionBehavior(QTableWidget.SelectRows) # type: ignore
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # type: ignore
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        btn_aggiungi = QPushButton("Aggiungi Ingrediente")
        btn_aggiungi.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white;
                border-radius: 10px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #66BB6A; }
        """)
        btn_aggiungi.clicked.connect(self.aggiungi_ingrediente)

        btn_scorte = QPushButton("Aggiorna Scorte")
        btn_scorte.setStyleSheet("""
            QPushButton {
                background-color: #FF9800; color: white;
                border-radius: 10px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #FFB74D; }
        """)
        btn_scorte.clicked.connect(self.aggiorna_scorte)

        btn_elimina = QPushButton("Rimuovi Ingrediente")
        btn_elimina.setStyleSheet("""
            QPushButton {
                background-color: #F44336; color: white;
                border-radius: 10px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #EF5350; }
        """)
        btn_elimina.clicked.connect(self.elimina_ingrediente)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_aggiungi)
        btn_layout.addWidget(btn_scorte)
        btn_layout.addWidget(btn_elimina)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        try:
            self.inventario_data = StaffAPIClient.get_inventario()
            self.table.setRowCount(len(self.inventario_data))

            alert_count = 0
            for row, item in enumerate(self.inventario_data):
                stato = item.get("stato", "")
                colore = COLORI_STATO_INVENTARIO.get(stato, QColor("#000000"))

                self.table.setItem(row, 0, QTableWidgetItem(str(item.get("id", ""))))
                self.table.setItem(row, 1, QTableWidgetItem(item.get("nome", "")))
                self.table.setItem(row, 2, QTableWidgetItem(str(item.get("quantita_disponibile", ""))))
                self.table.setItem(row, 3, QTableWidgetItem(item.get("unita_misura", "")))
                self.table.setItem(row, 4, QTableWidgetItem(str(item.get("soglia_minima", ""))))
                self.table.setItem(row, 5, QTableWidgetItem(str(item.get("categoria_id", ""))))

                item_stato = QTableWidgetItem(stato)
                item_stato.setForeground(colore)
                self.table.setItem(row, 6, item_stato)

                if stato in ("IN_ESAURIMENTO", "ESAURITO"):
                    alert_count += 1
                    for col in range(7):
                        cell = self.table.item(row, col)
                        if cell:
                            cell.setBackground(QColor("#FFF3E0") if stato == "IN_ESAURIMENTO" else QColor("#FFEBEE"))

            if alert_count > 0:
                self.lbl_alert.setText(f"⚠ {alert_count} ingrediente/i sotto scorta!")
            else:
                self.lbl_alert.setText("✓ Scorte nella norma")
                self.lbl_alert.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 13px;")

        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile caricare l'inventario:\n{e}")

    def aggiungi_ingrediente(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nuovo Ingrediente")
        dialog.setMinimumWidth(400)

        form = QFormLayout()
        campi = {}
        for campo, label in [("nome", "Nome:"), ("descrizione", "Descrizione:"),
                              ("quantita_disponibile", "Quantità:"), ("unita_misura", "Unità di misura:"),
                              ("soglia_minima", "Soglia minima:"), ("categoria_id", "Categoria ID:")]:
            input_field = QLineEdit()
            campi[campo] = input_field
            form.addRow(label, input_field)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  # type: ignore
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        dialog.setLayout(form)

        if dialog.exec_() == QDialog.Accepted:
            dati = {campo: input_field.text() for campo, input_field in campi.items()}
            try:
                StaffAPIClient.aggiungi_ingrediente(dati)
                QMessageBox.information(self, "Successo", "Ingrediente aggiunto.")
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def aggiorna_scorte(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un ingrediente dalla tabella.")
            return

        item = self.inventario_data[row]
        from PyQt5.QtWidgets import QInputDialog
        quantita, ok = QInputDialog.getDouble(
            self, "Aggiorna Scorte",
            f"Ingrediente: {item.get('nome')}\nQuantità attuale: {item.get('quantita_disponibile')} {item.get('unita_misura')}\n\nNuova quantità:",
            float(item.get("quantita_disponibile", 0)), 0, 99999, 1
        )

        if ok:
            try:
                success = StaffAPIClient.aggiorna_scorte(item.get("id"), quantita)
                if success:
                    QMessageBox.information(self, "Successo", "Scorte aggiornate.")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile aggiornare le scorte.")
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def elimina_ingrediente(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un ingrediente dalla tabella.")
            return

        item = self.inventario_data[row]
        risposta = QMessageBox.question(
            self, "Conferma Eliminazione",
            f"Eliminare l'ingrediente '{item.get('nome')}'?",
            QMessageBox.Yes | QMessageBox.No # type: ignore
        )

        if risposta == QMessageBox.Yes:
            try:
                success = StaffAPIClient.elimina_ingrediente(item.get("id"))
                if success:
                    QMessageBox.information(self, "Successo", "Ingrediente eliminato.")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile eliminare l'ingrediente.")
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))
