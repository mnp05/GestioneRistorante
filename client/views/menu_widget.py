from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from client.api_client import APIClient

class MenuWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.piatti_data = []
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Barra superiore (Categoria e Ricerca)
        search_layout = QHBoxLayout()
        
        lbl_cat = QLabel("Categoria:")
        # In una versione reale ci sarebbe una QComboBox qui
        search_layout.addWidget(lbl_cat)
        search_layout.addStretch()
        
        lbl_cerca = QLabel("Cerca piatto:")
        self.input_cerca = QLineEdit()
        self.input_cerca.setStyleSheet("border: 1px dashed black;")
        search_layout.addWidget(lbl_cerca)
        search_layout.addWidget(self.input_cerca)

        layout.addLayout(search_layout)

        # Tabella
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nome Piatto", "Costo", "Allergeni", "Ingredienti"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
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
            self.piatti_data = APIClient.get_menu()
            self.table.setRowCount(len(self.piatti_data))
            for row, piatto in enumerate(self.piatti_data):
                self.table.setItem(row, 0, QTableWidgetItem(piatto.get("nome", "")))
                self.table.setItem(row, 1, QTableWidgetItem(f"€{piatto.get('prezzo', '')}"))
                self.table.setItem(row, 2, QTableWidgetItem(piatto.get("allergeni", "")))
                self.table.setItem(row, 3, QTableWidgetItem(piatto.get("descrizione", "")))
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile caricare il menù:\n{e}")

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
