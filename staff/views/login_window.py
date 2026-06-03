from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from staff.api_client import StaffAPIClient


class StaffLoginWindow(QWidget):
    def __init__(self, on_login_callback):
        super().__init__()
        self.on_login_callback = on_login_callback
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Gestione Ristorante - Accesso Staff")
        self.resize(500, 400)
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("Area Staff")
        header.setAlignment(Qt.AlignCenter) # type: ignore
        header.setStyleSheet("""
            background-color: #8C1515;
            color: white;
            font-size: 32px;
            font-weight: bold;
            padding: 15px;
        """)
        layout.addWidget(header)

        subtitle = QLabel("Accesso riservato a Dipendenti e Gestori")
        subtitle.setAlignment(Qt.AlignCenter) # type: ignore
        subtitle.setStyleSheet("color: gray; font-style: italic; font-size: 13px;")
        layout.addWidget(subtitle)

        form_layout = QVBoxLayout()

        user_layout = QHBoxLayout()
        user_label = QLabel("Email:")
        self.user_input = QLineEdit()
        self.user_input.setStyleSheet("border: 1px dashed black; padding: 5px;")
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_input)

        pass_layout = QHBoxLayout()
        pass_label = QLabel("Password:")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password) # type: ignore
        self.pass_input.setStyleSheet("border: 1px dashed black; padding: 5px;")
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.pass_input)

        form_layout.addLayout(user_layout)
        form_layout.addLayout(pass_layout)
        layout.addLayout(form_layout)

        self.btn_accedi = QPushButton("Accedi")
        self.btn_accedi.setStyleSheet("""
            QPushButton {
                background-color: #8C1515;
                color: white;
                border-radius: 15px;
                padding: 10px 30px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #A31F1F; }
        """)
        self.btn_accedi.clicked.connect(self.handle_login)
        layout.addWidget(self.btn_accedi, alignment=Qt.AlignCenter) # type: ignore

        btn_recupera_password = QPushButton("Password dimenticata?")
        btn_recupera_password.setStyleSheet("color: #8C1515; text-decoration: underline; background: transparent; border: none;")
        btn_recupera_password.setCursor(Qt.PointingHandCursor) # type: ignore
        btn_recupera_password.clicked.connect(self.handle_recupera_password)
        layout.addWidget(btn_recupera_password, alignment=Qt.AlignCenter) # type: ignore

        layout.addStretch()
        self.setLayout(layout)

    def handle_login(self):
        email = self.user_input.text()
        password = self.pass_input.text()
        try:
            user_data = StaffAPIClient.login(email, password)
            if user_data.get("ruolo") not in ["Dipendente", "Gestore"]:
                QMessageBox.warning(self, "Accesso Negato", "Questa applicazione è riservata allo Staff.")
                return
            self.on_login_callback(user_data)
        except Exception as e:
            QMessageBox.critical(self, "Errore Accesso", str(e))

    def handle_recupera_password(self):
        from PyQt5.QtWidgets import QInputDialog
        email, ok = QInputDialog.getText(self, "Recupero Password Staff", "Inserisci la tua email lavorativa:")
        if ok and email.strip():
            try:
                pw = StaffAPIClient.recupera_password(email.strip())
                msg = f"📩 DA: noreply-staff@ristorante.it\nA: {email.strip()}\n\nRichiesta di recupero credenziali DIPENDENTE/GESTORE.\nLa tua password di accesso è: {pw}\n\nNon inoltrare mai questa email."
                QMessageBox.information(self, "E-mail Ricevuta (Simulazione)", msg)
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))
