from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QLineEdit, QFormLayout,
                             QDialog, QDialogButtonBox, QComboBox)
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

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        titolo = QLabel("Gestione Dipendenti (Solo Gestore)")
        titolo.setStyleSheet("font-size: 14px; font-weight: bold; color: #555;")
        layout.addWidget(titolo)

        info = QLabel("Da qui puoi creare nuovi account per i dipendenti del ristorante.")
        info.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info)

        layout.addSpacing(20)

        form_frame = QWidget()
        form_frame.setStyleSheet("background-color: #FAFAFA; border: 1px solid #E0E0E0; border-radius: 8px;")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)

        self.input_nome = QLineEdit()
        self.input_nome.setStyleSheet("border: 1px solid #CCC; padding: 5px; background-color: white;")
        form_layout.addRow("Nome:", self.input_nome)

        self.input_cognome = QLineEdit()
        self.input_cognome.setStyleSheet("border: 1px solid #CCC; padding: 5px; background-color: white;")
        form_layout.addRow("Cognome:", self.input_cognome)

        self.input_email = QLineEdit()
        self.input_email.setStyleSheet("border: 1px solid #CCC; padding: 5px; background-color: white;")
        self.input_email.setPlaceholderText("esempio@ristorante.it")
        form_layout.addRow("Email:", self.input_email)

        self.input_password = QLineEdit()
        self.input_password.setStyleSheet("border: 1px solid #CCC; padding: 5px; background-color: white;")
        self.input_password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.input_password)

        self.combo_livello = QComboBox()
        self.combo_livello.addItems(LIVELLI_ACCESSO)
        self.combo_livello.setStyleSheet("border: 1px solid #CCC; padding: 5px; background-color: white;")
        form_layout.addRow("Livello Accesso:", self.combo_livello)

        layout.addWidget(form_frame)

        btn_crea = QPushButton("Crea Account Dipendente")
        btn_crea.setStyleSheet("""
            QPushButton {
                background-color: #8C1515; color: white;
                border-radius: 15px; padding: 12px 30px;
                font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #A31F1F; }
        """)
        btn_crea.clicked.connect(self.crea_dipendente)
        layout.addWidget(btn_crea, alignment=Qt.AlignCenter)

        layout.addStretch()
        self.setLayout(layout)

    def crea_dipendente(self):
        nome = self.input_nome.text().strip()
        cognome = self.input_cognome.text().strip()
        email = self.input_email.text().strip()
        password = self.input_password.text()
        livello = self.combo_livello.currentText()

        if not all([nome, cognome, email, password]):
            QMessageBox.warning(self, "Attenzione", "Compila tutti i campi.")
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
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e))
