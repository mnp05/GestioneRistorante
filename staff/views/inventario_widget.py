from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QLineEdit, QFormLayout,
                             QDialog, QDialogButtonBox, QComboBox)
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
        self.categorie_disponibili = []
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
                border-radius: 5px; padding: 6px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #A31F1F; }
        """)
        btn_refresh.clicked.connect(self.load_data)
        top_layout.addWidget(btn_refresh)
        layout.addLayout(top_layout)

        # Barra Filtro
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtra per Categoria:"))
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItem("Tutte")
        self.combo_filtro.currentTextChanged.connect(self.applica_filtro)
        filter_layout.addWidget(self.combo_filtro)
        
        filter_layout.addSpacing(10)
        filter_layout.addWidget(QLabel("Cerca:"))
        self.inp_ricerca = QLineEdit()
        self.inp_ricerca.setPlaceholderText("Cerca ingrediente...")
        self.inp_ricerca.textChanged.connect(self.applica_filtro)
        filter_layout.addWidget(self.inp_ricerca)
        
        btn_elimina_cat = QPushButton("Elimina Categoria Attuale")
        btn_elimina_cat.setStyleSheet("background-color: #F44336; color: white; border-radius: 5px; padding: 4px 8px;")
        btn_elimina_cat.clicked.connect(self.elimina_categoria)
        filter_layout.addWidget(btn_elimina_cat)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nome", "Quantità", "Unità", "Soglia Min.", "Categoria", "Stato"
        ])
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.Stretch)     
        self.table.setSelectionBehavior(QTableWidget.SelectRows) 
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  
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

        btn_modifica = QPushButton("Modifica Ingrediente")
        btn_modifica.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; color: white;
                border-radius: 10px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #42A5F5; }
        """)
        btn_modifica.clicked.connect(self.modifica_ingrediente)

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
        btn_layout.addWidget(btn_modifica)
        btn_layout.addWidget(btn_scorte)
        btn_layout.addWidget(btn_elimina)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        try:
            self.inventario_data = StaffAPIClient.get_inventario()
            self.categorie_disponibili = StaffAPIClient.get_categorie_inventario()
            
            # Aggiorna il filtro
            filtro_attuale = self.combo_filtro.currentText()
            self.combo_filtro.blockSignals(True)
            self.combo_filtro.clear()
            self.combo_filtro.addItem("Tutte")
            self.combo_filtro.addItems(self.categorie_disponibili)
            if filtro_attuale in self.categorie_disponibili:
                self.combo_filtro.setCurrentText(filtro_attuale)
            else:
                self.combo_filtro.setCurrentIndex(0)
            self.combo_filtro.blockSignals(False)
            
            self.applica_filtro()
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile caricare l'inventario:\n{e}")

    def applica_filtro(self):
        categoria_filtro = self.combo_filtro.currentText()
        testo_ricerca = self.inp_ricerca.text().lower().strip()
        dati_filtrati = self.inventario_data
        
        if categoria_filtro != "Tutte":
            dati_filtrati = [i for i in dati_filtrati if i.get("categoria_id", "") == categoria_filtro]
            
        if testo_ricerca:
            dati_filtrati = [i for i in dati_filtrati if testo_ricerca in i.get("nome", "").lower() or testo_ricerca in i.get("descrizione", "").lower()]
            
        self.table.setRowCount(len(dati_filtrati))
        alert_count = 0
        
        for row, item in enumerate(dati_filtrati):
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

    def elimina_categoria(self):
        cat = self.combo_filtro.currentText()
        if cat == "Tutte" or not cat:
            QMessageBox.warning(self, "Attenzione", "Seleziona una categoria specifica dal filtro prima di eliminarla.")
            return
            
        risposta = QMessageBox.question(self, "Conferma", 
                                        f"Sei sicuro di voler eliminare la categoria '{cat}'? Verrà rimossa da tutti i prodotti.",
                                        QMessageBox.Yes | QMessageBox.No) 
        if risposta == QMessageBox.Yes:
            try:
                StaffAPIClient.elimina_categoria_inventario(cat)
                QMessageBox.information(self, "Successo", "Categoria eliminata con successo.")
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def aggiungi_ingrediente(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nuovo Ingrediente")
        dialog.setMinimumWidth(400)

        form = QFormLayout()
        campi = {}
        
        # Campi testuali standard
        for campo, label in [("nome", "Nome:"), ("descrizione", "Descrizione:"),
                              ("quantita_disponibile", "Quantità:"), ("unita_misura", "Unità di misura:"),
                              ("soglia_minima", "Soglia minima:")]:
            input_field = QLineEdit()
            campi[campo] = input_field
            form.addRow(label, input_field)
            
        # Categoria Editabile (Combo box)
        combo_categoria = QComboBox()
        combo_categoria.setEditable(True)
        combo_categoria.addItems(self.categorie_disponibili)
        combo_categoria.setToolTip("Seleziona o digita una nuova categoria")
        form.addRow("Categoria:", combo_categoria)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        dialog.setLayout(form)

        if dialog.exec_() == QDialog.Accepted:
            dati = {campo: input_field.text() for campo, input_field in campi.items()}
            dati["categoria_id"] = combo_categoria.currentText().strip()
            
            try:
                StaffAPIClient.aggiungi_ingrediente(dati)
                QMessageBox.information(self, "Successo", "Ingrediente aggiunto.")
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def modifica_ingrediente(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un ingrediente dalla tabella.")
            return

        id_item = self.table.item(row, 0).text() 
        item = next((i for i in self.inventario_data if str(i["id"]) == id_item), None)
        if not item: return

        dialog = QDialog(self)
        dialog.setWindowTitle("Modifica Ingrediente")
        form = QFormLayout()
        
        campi = {}
        
        for campo, label in [("nome", "Nome:"), ("descrizione", "Descrizione:"),
                              ("quantita_disponibile", "Quantità:"), ("unita_misura", "Unità di misura:"),
                              ("soglia_minima", "Soglia minima:")]:
            input_field = QLineEdit()
            input_field.setText(str(item.get(campo, "")))
            campi[campo] = input_field
            form.addRow(label, input_field)
            
        combo_categoria = QComboBox()
        combo_categoria.setEditable(True)
        combo_categoria.addItems(self.categorie_disponibili)
        combo_categoria.setCurrentText(str(item.get("categoria_id", "")))
        form.addRow("Categoria:", combo_categoria)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        dialog.setLayout(form)

        if dialog.exec_() == QDialog.Accepted:
            dati = {campo: input_field.text() for campo, input_field in campi.items()}
            dati["categoria_id"] = combo_categoria.currentText().strip()
            
            try:
                success = StaffAPIClient.modifica_ingrediente(id_item, dati)
                if success:
                    QMessageBox.information(self, "Successo", "Ingrediente modificato.")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile modificare l'ingrediente.")
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def aggiorna_scorte(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un ingrediente dalla tabella.")
            return

        id_item = self.table.item(row, 0).text() 
        item = next((i for i in self.inventario_data if str(i["id"]) == id_item), None)
        if not item: return

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

        id_item = self.table.item(row, 0).text() 
        item = next((i for i in self.inventario_data if str(i["id"]) == id_item), None)
        if not item: return

        risposta = QMessageBox.question(
            self, "Conferma Eliminazione",
            f"Eliminare l'ingrediente '{item.get('nome')}'?",
            QMessageBox.Yes | QMessageBox.No 
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
