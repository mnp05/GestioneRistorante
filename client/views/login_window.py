from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from client.api_client import APIClient

class LoginWindow(QWidget):
    def __init__(self, main_app_callback):
        super().__init__()
        self.main_app_callback = main_app_callback
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Accesso Ristorante")
        self.resize(500, 400)
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Intestazione Rossa
        header = QLabel("Accedi")
        header.setAlignment(Qt.AlignCenter)  # type: ignore
        header.setStyleSheet("""
            background-color: #8C1515; 
            color: white; 
            font-size: 32px; 
            font-weight: bold; 
            padding: 15px;
        """)
        layout.addWidget(header)

        # Spazio finto per il logo
        logo_placeholder = QLabel("[ LOGO ]")
        logo_placeholder.setAlignment(Qt.AlignCenter)  # type: ignore
        logo_placeholder.setStyleSheet("border: 1px solid black; font-size: 20px; padding: 20px;")
        layout.addWidget(logo_placeholder)

        # Form di Login
        form_layout = QVBoxLayout()
        
        user_layout = QHBoxLayout()
        user_label = QLabel("Nome Utente / Email:")
        self.user_input = QLineEdit()
        self.user_input.setStyleSheet("border: 1px dashed black; padding: 5px;")
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_input)
        
        pass_layout = QHBoxLayout()
        pass_label = QLabel("Password:")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet("border: 1px dashed black; padding: 5px;")
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.pass_input)

        form_layout.addLayout(user_layout)
        form_layout.addLayout(pass_layout)
        layout.addLayout(form_layout)

        # Pulsanti
        btn_layout = QHBoxLayout()
        self.btn_accedi = QPushButton("Accedi")
        self.btn_registrati = QPushButton("Registrati")
        
        btn_style = """
            QPushButton {
                background-color: #8C1515;
                color: white;
                border-radius: 15px;
                padding: 10px 30px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #A31F1F; }
        """
        self.btn_accedi.setStyleSheet(btn_style)
        self.btn_registrati.setStyleSheet(btn_style)
        
        self.btn_accedi.clicked.connect(self.handle_login)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_accedi)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(self.btn_registrati)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Nota
        note = QLabel("NOTA: Registrati per accumulare punti fedeltà ed utilizzare i Buoni Regalo!")
        note.setAlignment(Qt.AlignCenter)  # type: ignore
        note.setStyleSheet("color: gray; font-style: italic; border: 1px solid gray; padding: 10px;")
        layout.addWidget(note)

        layout.addStretch()
        self.setLayout(layout)

    def handle_login(self):
        email = self.user_input.text()
        password = self.pass_input.text()
        try:
            user_data = APIClient.login(email, password)
            self.main_app_callback(user_data) # Passiamo al Main Window
        except Exception as e:
            QMessageBox.critical(self, "Errore Accesso", str(e))
