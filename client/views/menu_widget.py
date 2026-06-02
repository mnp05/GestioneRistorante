from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt
from client.api_client import APIClient

class MenuWidget(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.piatti_data = []
        self.preferiti_ids = []
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Barra superiore (Ricerca e Preferiti)
        search_layout = QHBoxLayout()
        
        self.chk_preferiti = QCheckBox("Mostra solo i miei Preferiti")
        self.chk_preferiti.setStyleSheet("color: #8C1515; font-weight: bold;")
        self.chk_preferiti.stateChanged.connect(self.load_data)
        search_layout.addWidget(self.chk_preferiti)
        
        search_layout.addStretch()
        
        lbl_cerca = QLabel("Cerca piatto:")
        self.input_cerca = QLineEdit()
        self.input_cerca.setStyleSheet("border: 1px dashed black; padding: 5px;")
        search_layout.addWidget(lbl_cerca)
        search_layout.addWidget(self.input_cerca)

        layout.addLayout(search_layout)

        # Tabella
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Preferito", "Nome Piatto", "Costo", "Allergeni", "Ingredienti"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # type: ignore
        # Fix column 0 width for the heart button
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # type: ignore
        self.table.setSelectionBehavior(QTableWidget.SelectRows) # type: ignore
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # type: ignore
        layout.addWidget(self.table)

        # Pulsante Dettagli
        self.btn_dettagli = QPushButton("[VEDI DETTAGLI PIATTO E RICETTA]")
        self.btn_dettagli.setStyleSheet("""
            QPushButton {
                background-color: #FFF0E6;
                color: #555;
                border: 1px solid #E0E0E0;
                padding: 15px;
            }
            QPushButton:hover { background-color: #FFE4D6; }
        """)
        self.btn_dettagli.clicked.connect(self.mostra_dettagli)
        layout.addWidget(self.btn_dettagli)

        self.setLayout(layout)

    def load_data(self):
        try:
            user_id = self.user_data.get("id")
            preferiti_data = APIClient.get_preferiti(user_id)
            self.preferiti_ids = [str(p.get("id")) for p in preferiti_data]
            
            if self.chk_preferiti.isChecked():
                self.piatti_data = preferiti_data
            else:
                self.piatti_data = APIClient.get_menu()
                
            self.table.setRowCount(len(self.piatti_data))
            for row, piatto in enumerate(self.piatti_data):
                piatto_id = str(piatto.get("id"))
                
                # Bottone Preferito (Cuore)
                btn_fav = QPushButton()
                if piatto_id in self.preferiti_ids:
                    btn_fav.setText("❤")
                    btn_fav.setStyleSheet("color: red; font-size: 16px; border: none; background: transparent;")
                else:
                    btn_fav.setText("♡")
                    btn_fav.setStyleSheet("color: gray; font-size: 16px; border: none; background: transparent;")
                    
                btn_fav.clicked.connect(lambda checked, pid=piatto_id: self.toggle_fav(pid))
                self.table.setCellWidget(row, 0, btn_fav)
                
                self.table.setItem(row, 1, QTableWidgetItem(piatto.get("nome", "")))
                self.table.setItem(row, 2, QTableWidgetItem(f"€{piatto.get('prezzo', '')}"))
                self.table.setItem(row, 3, QTableWidgetItem(piatto.get("allergeni", "")))
                self.table.setItem(row, 4, QTableWidgetItem(piatto.get("descrizione", "")))
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile caricare il menù:\n{e}")

    def toggle_fav(self, piatto_id):
        try:
            APIClient.toggle_preferito(self.user_data.get("id"), piatto_id)
            self.load_data()
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile aggiornare i preferiti:\n{e}")

    def mostra_dettagli(self):
        selected = self.table.currentRow()
        if selected >= 0:
            piatto = self.piatti_data[selected]
            QMessageBox.information(
                self, 
                "Dettagli Ricetta", 
                f"Piatto: {piatto.get('nome')}\nPrezzo: €{piatto.get('prezzo')}\n\nDescrizione/Ricetta:\n{piatto.get('descrizione')}"
            )
        else:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un piatto dalla tabella.")
