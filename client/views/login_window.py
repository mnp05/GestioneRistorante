from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QStackedWidget,
                             QFormLayout)
from PyQt5.QtCore import Qt
from client.api_client import APIClient

class LoginWindow(QWidget):
    def __init__(self, main_app_callback):
        super().__init__()
        self.main_app_callback = main_app_callback
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Ristorante - Accesso Cliente")
        self.resize(500, 450)
        self.setStyleSheet("background-color: white;")

        self.stacked_widget = QStackedWidget(self)
        
        # Creazione delle due viste
        self.login_view = self.create_login_view()
        self.register_view = self.create_register_view()
        
        self.stacked_widget.addWidget(self.login_view)
        self.stacked_widget.addWidget(self.register_view)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def create_login_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        header = QLabel("Accedi")
        header.setAlignment(Qt.AlignCenter)  
        header.setStyleSheet("background-color: #8C1515; color: white; font-size: 32px; font-weight: bold; padding: 15px;")
        layout.addWidget(header)

        logo_placeholder = QLabel("[ LOGO ]")
        logo_placeholder.setAlignment(Qt.AlignCenter)  
        logo_placeholder.setStyleSheet("border: 1px solid black; font-size: 20px; padding: 20px;")
        layout.addWidget(logo_placeholder)

        form_layout = QFormLayout()
        
        self.user_input = QLineEdit()
        self.user_input.setStyleSheet("border: 1px dashed black; padding: 5px;")
        form_layout.addRow("Email:", self.user_input)
        
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password) 
        self.pass_input.setStyleSheet("border: 1px dashed black; padding: 5px;")
        form_layout.addRow("Password:", self.pass_input)

        layout.addLayout(form_layout)

        btn_style = """
            QPushButton {
                background-color: #8C1515; color: white; border-radius: 15px; padding: 10px 30px; font-weight: bold;
            }
            QPushButton:hover { background-color: #A31F1F; }
        """
        
        btn_layout = QHBoxLayout()
        btn_accedi = QPushButton("Accedi")
        btn_accedi.setStyleSheet(btn_style)
        btn_accedi.clicked.connect(self.handle_login)
        
        btn_vai_a_registrati = QPushButton("Registrati")
        btn_vai_a_registrati.setStyleSheet(btn_style)
        btn_vai_a_registrati.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        btn_layout.addStretch()
        btn_layout.addWidget(btn_accedi)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(btn_vai_a_registrati)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)

        btn_recupera_password = QPushButton("Password dimenticata?")
        btn_recupera_password.setStyleSheet("color: #8C1515; text-decoration: underline; background: transparent; border: none;")
        btn_recupera_password.setCursor(Qt.PointingHandCursor) 
        btn_recupera_password.clicked.connect(self.handle_recupera_password)
        layout.addWidget(btn_recupera_password, alignment=Qt.AlignCenter) 

        note = QLabel("NOTA: Registrati per accumulare punti fedeltà ed utilizzare i Buoni Regalo!")
        note.setAlignment(Qt.AlignCenter)  
        note.setStyleSheet("color: gray; font-style: italic; border: 1px solid gray; padding: 10px;")
        layout.addWidget(note)

        layout.addStretch()
        return view

    def create_register_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        header = QLabel("Crea un Nuovo Account")
        header.setAlignment(Qt.AlignCenter)  
        header.setStyleSheet("background-color: #E6D2B5; color: #8C1515; font-size: 28px; font-weight: bold; padding: 15px;")
        layout.addWidget(header)

        form_layout = QFormLayout()
        
        self.reg_nome = QLineEdit()
        self.reg_nome.setStyleSheet("border: 1px solid #8C1515; padding: 5px;")
        form_layout.addRow("Nome:", self.reg_nome)

        self.reg_cognome = QLineEdit()
        self.reg_cognome.setStyleSheet("border: 1px solid #8C1515; padding: 5px;")
        form_layout.addRow("Cognome:", self.reg_cognome)

        self.reg_email = QLineEdit()
        self.reg_email.setStyleSheet("border: 1px solid #8C1515; padding: 5px;")
        form_layout.addRow("Email:", self.reg_email)
        
        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.Password) 
        self.reg_password.setStyleSheet("border: 1px solid #8C1515; padding: 5px;")
        form_layout.addRow("Password:", self.reg_password)

        layout.addLayout(form_layout)

        btn_style = """
            QPushButton {
                background-color: #8C1515; color: white; border-radius: 15px; padding: 10px 30px; font-weight: bold;
            }
            QPushButton:hover { background-color: #A31F1F; }
        """
        btn_style_alt = """
            QPushButton {
                background-color: gray; color: white; border-radius: 15px; padding: 10px 30px; font-weight: bold;
            }
            QPushButton:hover { background-color: darkgray; }
        """
        
        btn_layout = QHBoxLayout()
        btn_registrati = QPushButton("Conferma")
        btn_registrati.setStyleSheet(btn_style)
        btn_registrati.clicked.connect(self.handle_register)
        
        btn_indietro = QPushButton("Indietro")
        btn_indietro.setStyleSheet(btn_style_alt)
        btn_indietro.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        btn_layout.addStretch()
        btn_layout.addWidget(btn_indietro)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(btn_registrati)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        return view

    def handle_login(self):
        email = self.user_input.text().strip()
        password = self.pass_input.text()
        try:
            user_data = APIClient.login(email, password)
            self.main_app_callback(user_data)
        except Exception as e:
            QMessageBox.critical(self, "Errore Accesso", str(e))

    def handle_recupera_password(self):
        from PyQt5.QtWidgets import QInputDialog, QDialog, QFormLayout, QDialogButtonBox
        email, ok = QInputDialog.getText(self, "Recupero Password", "Inserisci l'indirizzo email associato al tuo account:")
        if ok and email.strip():
            try:
                # 3. Chiamata API per generare il codice temporaneo
                code = APIClient.recupera_password(email.strip())
                
                # 4. Simulazione invio email
                msg = f"📩 DA: noreply@ristorante.it\nA: {email.strip()}\n\nAbbiamo ricevuto una richiesta di recupero per le tue credenziali.\nIl tuo codice temporaneo è: {code}\n\nInseriscilo nella schermata del programma per scegliere una nuova password."
                QMessageBox.information(self, "E-mail Ricevuta (Simulazione)", msg)
                
                # 5. Dialogo per inserire Codice + Nuova Password
                dialog = QDialog(self)
                dialog.setWindowTitle("Reimposta Password")
                dialog.resize(300, 150)
                layout = QFormLayout(dialog)
                
                input_code = QLineEdit()
                layout.addRow("Codice ricevuto:", input_code)
                
                input_new_pw = QLineEdit()
                input_new_pw.setEchoMode(QLineEdit.Password)
                layout.addRow("Nuova Password:", input_new_pw)
                
                button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                button_box.accepted.connect(dialog.accept)
                button_box.rejected.connect(dialog.reject)
                layout.addWidget(button_box)
                
                if dialog.exec_() == QDialog.Accepted:
                    try:
                        # 6. Aggiornamento
                        APIClient.reset_password(email.strip(), input_code.text().strip(), input_new_pw.text())
                        QMessageBox.information(self, "Successo", "Password reimpostata con successo! Ora puoi accedere.")
                    except Exception as reset_e:
                        QMessageBox.critical(self, "Errore Reset", str(reset_e))
                        
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def handle_register(self):
        nome = self.reg_nome.text().strip()
        cognome = self.reg_cognome.text().strip()
        email = self.reg_email.text().strip()
        password = self.reg_password.text()

        if not all([nome, cognome, email, password]):
            QMessageBox.warning(self, "Attenzione", "Tutti i campi sono obbligatori.")
            return
            
        if "@" not in email:
            QMessageBox.warning(self, "Attenzione", "Inserisci un indirizzo email valido (deve contenere la '@').")
            return

        try:
            user_data = APIClient.register(nome, cognome, email, password)
            QMessageBox.information(self, "Benvenuto!", f"Account creato con successo, {nome}!\nEffettuo l'accesso automatico...")
            self.main_app_callback(user_data)
        except Exception as e:
            QMessageBox.critical(self, "Errore Registrazione", str(e))
