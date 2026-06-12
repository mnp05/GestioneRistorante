from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QLineEdit, QFormLayout,
                             QInputDialog, QComboBox, QGroupBox)
from PyQt5.QtCore import Qt
from staff.api_client import StaffAPIClient

LIVELLI_ACCESSO = [
    "GESTIONE_PRENOTAZIONI",
    "GESTIONE_INVENTARIO",
    "GESTIONE_MENU",
    "ACCESSO_COMPLETO",
]

class DipendentiWidget(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- SINISTRA: Form Creazione ---
        left_panel = QGroupBox("Crea Nuovo Dipendente")
        left_panel.setStyleSheet("""
            QGroupBox { font-weight: bold; border: 1px solid #CCC; border-radius: 8px; margin-top: 15px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #8C1515; }
        """)
        form_layout = QFormLayout(left_panel)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(15, 25, 15, 15)

        self.input_nome = QLineEdit()
        self.input_nome.setStyleSheet("border: 1px solid #CCC; padding: 5px;")
        form_layout.addRow("Nome:", self.input_nome)

        self.input_cognome = QLineEdit()
        self.input_cognome.setStyleSheet("border: 1px solid #CCC; padding: 5px;")
        form_layout.addRow("Cognome:", self.input_cognome)

        self.input_email = QLineEdit()
        self.input_email.setStyleSheet("border: 1px solid #CCC; padding: 5px;")
        self.input_email.setPlaceholderText("esempio@ristorante.it")
        form_layout.addRow("Email:", self.input_email)

        self.input_password = QLineEdit()
        self.input_password.setStyleSheet("border: 1px solid #CCC; padding: 5px;")
        self.input_password.setEchoMode(QLineEdit.Password) 
        form_layout.addRow("Password:", self.input_password)

        self.combo_livello = QComboBox()
        self.combo_livello.addItems(LIVELLI_ACCESSO)
        self.combo_livello.setStyleSheet("border: 1px solid #CCC; padding: 5px;")
        form_layout.addRow("Livello Accesso:", self.combo_livello)

        btn_crea = QPushButton("Registra")
        btn_crea.setStyleSheet("background-color: #8C1515; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        btn_crea.clicked.connect(self.crea_dipendente)
        form_layout.addRow(btn_crea)

        # --- DESTRA: Lista Dipendenti ---
        right_panel = QGroupBox("Gestione Personale (Lista)")
        right_panel.setStyleSheet(left_panel.styleSheet())
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 25, 15, 15)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Cognome", "Ruolo", "Livello Accesso"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        self.table.setSelectionBehavior(QTableWidget.SelectRows) 
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) 
        right_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_aggiorna = QPushButton("Aggiorna")
        btn_modifica = QPushButton("Modifica Livello")
        btn_elimina = QPushButton("Elimina Account")
        
        btn_elimina.setStyleSheet("color: red; font-weight: bold;")

        btn_aggiorna.clicked.connect(self.load_data)
        btn_modifica.clicked.connect(self.modifica_livello)
        btn_elimina.clicked.connect(self.elimina_dipendente)

        btn_layout.addWidget(btn_aggiorna)
        btn_layout.addWidget(btn_modifica)
        btn_layout.addWidget(btn_elimina)
        right_layout.addLayout(btn_layout)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

    def load_data(self):
        self.table.setRowCount(0)
        try:
            dipendenti = StaffAPIClient.get_dipendenti()
            for d in dipendenti:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(d.get("id"))))
                self.table.setItem(row, 1, QTableWidgetItem(d.get("nome")))
                self.table.setItem(row, 2, QTableWidgetItem(d.get("cognome")))
                self.table.setItem(row, 3, QTableWidgetItem(d.get("ruolo")))
                self.table.setItem(row, 4, QTableWidgetItem(d.get("livello_accesso", "N/D")))
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile caricare i dipendenti:\n{e}")

    def crea_dipendente(self):
        nome = self.input_nome.text().strip()
        cognome = self.input_cognome.text().strip()
        email = self.input_email.text().strip()
        password = self.input_password.text()
        livello = self.combo_livello.currentText()

        if not all([nome, cognome, email, password]):
            QMessageBox.warning(self, "Attenzione", "Compila tutti i campi.")
            return

        if "@" not in email:
            QMessageBox.warning(self, "Attenzione", "L'email deve contenere una '@'.")
            return

        try:
            StaffAPIClient.crea_dipendente(
                self.user_data.get("id"), nome, cognome, email, password, livello
            )
            QMessageBox.information(self, "Successo", f"Account creato per {nome} {cognome}.")
            self.input_nome.clear()
            self.input_cognome.clear()
            self.input_email.clear()
            self.input_password.clear()
            self.load_data()
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e))

    def modifica_livello(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attenzione", "Seleziona un dipendente dalla lista.")
            return

        row = selected[0].row()
        dip_id = self.table.item(row, 0).text() 
        nome_completo = f"{self.table.item(row, 1).text()} {self.table.item(row, 2).text()}" 
        ruolo = self.table.item(row, 3).text() 

        if ruolo == "Gestore":
            QMessageBox.warning(self, "Negato", "Non puoi modificare il livello di un altro Gestore.")
            return

        livello, ok = QInputDialog.getItem(
            self, "Modifica Livello", f"Seleziona il nuovo livello per {nome_completo}:",
            LIVELLI_ACCESSO, 0, False
        )

        if ok and livello:
            try:
                StaffAPIClient.aggiorna_livello_dipendente(self.user_data.get("id"), dip_id, livello)
                QMessageBox.information(self, "Successo", "Livello aggiornato correttamente.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Errore", str(e))

    def elimina_dipendente(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attenzione", "Seleziona un dipendente dalla lista.")
            return

        row = selected[0].row()
        dip_id = self.table.item(row, 0).text() 
        nome_completo = f"{self.table.item(row, 1).text()} {self.table.item(row, 2).text()}" 

        risposta = QMessageBox.question(
            self, "Conferma Eliminazione",
            f"Vuoi davvero eliminare l'account di {nome_completo} in modo permanente?",
            QMessageBox.Yes | QMessageBox.No 
        )

        if risposta == QMessageBox.Yes:
            try:
                StaffAPIClient.elimina_dipendente(self.user_data.get("id"), dip_id)
                QMessageBox.information(self, "Successo", "Account eliminato.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Errore", str(e))
