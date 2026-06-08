from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QFrame,
                             QMessageBox, QLineEdit, QInputDialog)
from PyQt5.QtCore import Qt
from staff.api_client import StaffAPIClient

class StaffDashboardWidget(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # TITOLO IN ALTO
        top_layout = QHBoxLayout()
        titolo = QLabel("BACHECA MESSAGGI DI SERVIZIO:")
        titolo.setStyleSheet("font-size: 16px; font-weight: bold; color: #555;")
        top_layout.addWidget(titolo)
        top_layout.addStretch()

        btn_modifica_password = QPushButton("Modifica Password")
        btn_modifica_password.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; color: white;
                border-radius: 5px; padding: 6px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #42A5F5; }
        """)
        btn_modifica_password.clicked.connect(self.modifica_password)
        top_layout.addWidget(btn_modifica_password)

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

        # AREA MESSAGGI AL CENTRO
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.messaggi_container = QWidget()
        self.messaggi_layout = QVBoxLayout(self.messaggi_container)
        self.messaggi_layout.setAlignment(Qt.AlignTop) 
        scroll.setWidget(self.messaggi_container)

        layout.addWidget(scroll)

        # INSERIMENTO TESTO IN BASSO
        input_layout = QHBoxLayout()
        lbl_scrivi = QLabel("Scrivi Messaggio:")
        lbl_scrivi.setStyleSheet("color: #555;")
        input_layout.addWidget(lbl_scrivi)

        self.input_messaggio = QLineEdit()
        self.input_messaggio.setPlaceholderText("Scrivi qui il tuo messaggio...")
        self.input_messaggio.setStyleSheet("""
            QLineEdit {
                border: 2px dashed #555;
                padding: 8px;
                background-color: white;
            }
        """)
        input_layout.addWidget(self.input_messaggio)
        
        layout.addLayout(input_layout)

        # BOTTONE INVIA
        btn_invia_layout = QHBoxLayout()
        btn_invia_layout.addStretch()
        
        btn_pubblica = QPushButton("INVIA NOTA")
        btn_pubblica.setStyleSheet("""
            QPushButton {
                background-color: #8C0000; color: white;
                border-radius: 15px; padding: 10px 30px; font-weight: bold;
            }
            QPushButton:hover { background-color: #A30000; }
        """)
        btn_pubblica.clicked.connect(self.pubblica_messaggio)
        btn_invia_layout.addWidget(btn_pubblica)
        
        layout.addLayout(btn_invia_layout)

        self.setLayout(layout)

    def load_data(self):
        while self.messaggi_layout.count():
            child = self.messaggi_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        try:
            messaggi = StaffAPIClient.get_messaggi()
            if not messaggi:
                lbl_vuoto = QLabel("Nessun messaggio in bacheca.")
                lbl_vuoto.setStyleSheet("color: gray; font-style: italic; padding: 20px;")
                lbl_vuoto.setAlignment(Qt.AlignCenter) 
                self.messaggi_layout.addWidget(lbl_vuoto)
                return

            for msg in messaggi:
                card = self._crea_card_messaggio(msg)
                self.messaggi_layout.addWidget(card)

        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile caricare i messaggi:\n{e}")

    def _crea_card_messaggio(self, msg):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #E0E0E0;
                border: 1px solid #BDBDBD;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)

        header_layout = QHBoxLayout()
        
        ruolo = str(msg.get("ruolo_autore", "DIPENDENTE")).upper()
        nome = str(msg.get("nome_autore", "")).upper()
        cognome = str(msg.get("cognome_autore", "")).upper()
        
        lbl_autore = QLabel(f"DA: {ruolo} - {nome} {cognome}")
        lbl_autore.setStyleSheet("font-weight: bold; color: #555; border: none;")
        
        lbl_data = QLabel(msg.get("timestamp", ""))
        lbl_data.setStyleSheet("color: gray; font-size: 11px; border: none;")
        
        header_layout.addWidget(lbl_autore)
        header_layout.addStretch()
        header_layout.addWidget(lbl_data)

        lbl_testo = QLabel(msg.get("testo", ""))
        lbl_testo.setWordWrap(True)
        lbl_testo.setStyleSheet("border: none; padding: 5px 0; color: #333; font-size: 13px;")

        is_proprio = str(msg.get("utente_id")) == str(self.user_data.get("id"))
        is_gestore = self.user_data.get("ruolo") == "Gestore"

        card_layout.addLayout(header_layout)
        card_layout.addWidget(lbl_testo)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        if is_proprio:
            btn_modifica = QPushButton("Modifica")
            btn_modifica.setFixedWidth(60)
            btn_modifica.setStyleSheet("""
                QPushButton {
                    background-color: transparent; color: #2196F3;
                    text-decoration: underline; border: none; font-size: 11px;
                }
                QPushButton:hover { color: #0b7dda; }
            """)
            msg_id = msg.get("id")
            testo = msg.get("testo", "")
            btn_modifica.clicked.connect(lambda checked, mid=msg_id, txt=testo: self.modifica_messaggio(mid, txt))
            buttons_layout.addWidget(btn_modifica)

        if is_proprio or is_gestore:
            btn_elimina = QPushButton("Elimina")
            btn_elimina.setFixedWidth(80)
            btn_elimina.setStyleSheet("""
                QPushButton {
                    background-color: transparent; color: #F44336;
                    text-decoration: underline; border: none; font-size: 11px;
                }
                QPushButton:hover { color: #D32F2F; }
            """)
            msg_id = msg.get("id")
            btn_elimina.clicked.connect(lambda checked, mid=msg_id: self.elimina_messaggio(mid))
            buttons_layout.addWidget(btn_elimina)

        if is_proprio or is_gestore:
            card_layout.addLayout(buttons_layout)

        return card

    def pubblica_messaggio(self):
        testo = self.input_messaggio.text().strip()
        if not testo:
            QMessageBox.warning(self, "Attenzione", "Scrivi un messaggio prima di pubblicare.")
            return

        try:
            StaffAPIClient.pubblica_messaggio(self.user_data.get("id"), testo)
            self.input_messaggio.clear()
            self.load_data()
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e))

    def elimina_messaggio(self, msg_id):
        risposta = QMessageBox.question(
            self, "Conferma Eliminazione",
            "Eliminare questo messaggio?",
            QMessageBox.Yes | QMessageBox.No 
        )

        if risposta == QMessageBox.Yes:
            try:
                success = StaffAPIClient.elimina_messaggio(
                    msg_id, self.user_data.get("id"), self.user_data.get("ruolo")
                )
                if success:
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile eliminare il messaggio.")
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def modifica_messaggio(self, msg_id, testo_attuale):
        nuovo_testo, ok = QInputDialog.getMultiLineText(
            self, "Modifica Messaggio", "Testo del messaggio:", testo_attuale
        )
        if ok and nuovo_testo.strip():
            try:
                success = StaffAPIClient.modifica_messaggio(
                    msg_id, self.user_data.get("id"), nuovo_testo.strip()
                )
                if success:
                    self.load_data()
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def modifica_password(self):
        from PyQt5.QtWidgets import QInputDialog, QLineEdit
        old_pw, ok = QInputDialog.getText(self, "Modifica Password", "Inserisci la tua VECCHIA password:", QLineEdit.Password) 
        if not ok or not old_pw: return
        
        new_pw, ok2 = QInputDialog.getText(self, "Modifica Password", "Inserisci la NUOVA password:", QLineEdit.Password) 
        if not ok2 or not new_pw: return
        
        try:
            success = StaffAPIClient.cambia_password(self.user_data.get("id"), old_pw, new_pw)
            if success:
                QMessageBox.information(self, "Successo", "Password aggiornata correttamente.")
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e))
