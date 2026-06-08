from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
from PyQt5.QtCore import Qt
from client.api_client import APIClient

class DashboardWidget(QWidget):
    def __init__(self, user_data, logout_callback=None):
        super().__init__()
        self.user_data = user_data
        self.logout_callback = logout_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        welcome_label = QLabel("Benvenuto nella tua area personale!")
        welcome_label.setStyleSheet("font-size: 16px; font-weight: bold; color: gray;")
        layout.addWidget(welcome_label)

        # Contenitore delle due card gialle
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # Card Sinistra (Punti)
        card_punti = QFrame()
        card_punti.setStyleSheet("background-color: #FFFFE0; border: 1px solid #E0E0E0;")
        punti_layout = QVBoxLayout(card_punti)
        
        lbl_titolo_punti = QLabel("SALDO PUNTI FEDELTA'")
        lbl_titolo_punti.setAlignment(Qt.AlignCenter)  
        lbl_titolo_punti.setStyleSheet("color: #8C1515; font-weight: bold; border: none;")
        
        saldo = self.user_data.get("saldo_punti", 0)
        lbl_punti = QLabel(f"{saldo} Punti")
        lbl_punti.setAlignment(Qt.AlignCenter)  
        lbl_punti.setStyleSheet("font-size: 24px; font-weight: bold; border: none;")
        
        lbl_prossimo = QLabel("Prossimo premio a 100")
        lbl_prossimo.setAlignment(Qt.AlignCenter)  
        lbl_prossimo.setStyleSheet("color: gray; border: none;")

        punti_layout.addWidget(lbl_titolo_punti)
        punti_layout.addStretch()
        punti_layout.addWidget(lbl_punti)
        punti_layout.addStretch()
        punti_layout.addWidget(lbl_prossimo)

        # Card Destra (Info Buoni Regalo)
        card_buoni = QFrame()
        card_buoni.setStyleSheet("background-color: #FFFFE0; border: 1px solid #E0E0E0; border-radius: 8px;")
        buoni_layout = QVBoxLayout(card_buoni)
        
        lbl_titolo_buoni = QLabel("BUONI REGALO")
        lbl_titolo_buoni.setAlignment(Qt.AlignCenter) 
        lbl_titolo_buoni.setStyleSheet("color: #8C1515; font-weight: bold; border: none; font-size: 16px;")

        lbl_info = QLabel("Scopri i nostri Buoni Regalo!\n\nRegala un'esperienza gastronomica unica\no riscatta un codice ricevuto in dono.")
        lbl_info.setAlignment(Qt.AlignCenter) 
        lbl_info.setStyleSheet("border: none; color: #555; font-size: 14px;")

        lbl_cta = QLabel("Vai alla tab 'Buoni Regalo' in alto")
        lbl_cta.setAlignment(Qt.AlignCenter) 
        lbl_cta.setStyleSheet("font-style: italic; color: #888; border: none;")

        buoni_layout.addWidget(lbl_titolo_buoni)
        buoni_layout.addSpacing(10)
        buoni_layout.addWidget(lbl_info)
        buoni_layout.addSpacing(10)
        buoni_layout.addWidget(lbl_cta)

        cards_layout.addWidget(card_punti)
        cards_layout.addWidget(card_buoni)

        layout.addLayout(cards_layout)
        
        nota = QLabel("* I punti vengono accumulati automaticamente al pagamento di ciascuna prenotazione effettuata a tuo nome (1 punto per ogni euro speso).")
        nota.setStyleSheet("font-style: italic; color: gray;")
        nota.setWordWrap(True)
        layout.addSpacing(20)
        layout.addWidget(nota)

        layout.addStretch()
        
        # Zona Cancella Account
        danger_zone = QHBoxLayout()
        danger_zone.addStretch()
        
        btn_modifica_password = QPushButton("Modifica Password")
        btn_modifica_password.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #2196F3;
                border: 1px solid #2196F3;
                border-radius: 5px;
                padding: 6px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #E3F2FD; }
        """)
        btn_modifica_password.clicked.connect(self.modifica_password)
        danger_zone.addWidget(btn_modifica_password)
        
        danger_zone.addSpacing(10)
        
        btn_cancella_account = QPushButton("Elimina Account")
        btn_cancella_account.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #D45B5B;
                border: 1px solid #D45B5B;
                border-radius: 5px;
                padding: 6px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFF0F0;
            }
        """)
        btn_cancella_account.clicked.connect(self.conferma_cancella_account)
        danger_zone.addWidget(btn_cancella_account)
        
        layout.addLayout(danger_zone)

        self.setLayout(layout)

    def conferma_cancella_account(self):
        from PyQt5.QtWidgets import QInputDialog, QLineEdit
        password, ok = QInputDialog.getText(
            self, "Conferma Cancellazione",
            "Attenzione! L'eliminazione dell'account è irreversibile e perderai tutti i punti fedeltà.\n\nPer confermare, inserisci la tua password:",
            QLineEdit.Password 
        )

        if ok:
            if not password:
                QMessageBox.warning(self, "Errore", "Devi inserire la password per procedere.")
                return
                
            try:
                success = APIClient.cancella_account(self.user_data.get("id"), password)
                if success:
                    QMessageBox.information(self, "Addio", "Account eliminato con successo. Speriamo di rivederti!")
                    if self.logout_callback:
                        self.logout_callback()
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def modifica_password(self):
        from PyQt5.QtWidgets import QInputDialog, QLineEdit
        old_pw, ok = QInputDialog.getText(self, "Modifica Password", "Inserisci la tua VECCHIA password:", QLineEdit.Password) 
        if not ok or not old_pw: return
        
        new_pw, ok2 = QInputDialog.getText(self, "Modifica Password", "Inserisci la NUOVA password:", QLineEdit.Password) 
        if not ok2 or not new_pw: return
        
        try:
            success = APIClient.cambia_password(self.user_data.get("id"), old_pw, new_pw)
            if success:
                QMessageBox.information(self, "Successo", "Password aggiornata correttamente.")
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e))
