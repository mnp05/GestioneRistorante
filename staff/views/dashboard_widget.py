from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QScrollArea, QFrame,
                             QMessageBox)
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

        top_layout = QHBoxLayout()
        titolo = QLabel("Bacheca Messaggi Interni")
        titolo.setStyleSheet("font-size: 14px; font-weight: bold; color: #555;")
        top_layout.addWidget(titolo)
        top_layout.addStretch()

        btn_refresh = QPushButton("Aggiorna")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #8C1515; color: white;
                border-radius: 10px; padding: 6px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #A31F1F; }
        """)
        btn_refresh.clicked.connect(self.load_data)
        top_layout.addWidget(btn_refresh)
        layout.addLayout(top_layout)

        nuovo_msg_layout = QHBoxLayout()
        self.input_messaggio = QTextEdit()
        self.input_messaggio.setMaximumHeight(60)
        self.input_messaggio.setPlaceholderText("Scrivi un messaggio per lo staff...")
        self.input_messaggio.setStyleSheet("border: 1px solid #E0E0E0; padding: 5px;")

        btn_pubblica = QPushButton("Pubblica")
        btn_pubblica.setFixedHeight(60)
        btn_pubblica.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white;
                border-radius: 10px; padding: 8px 20px; font-weight: bold;
            }
            QPushButton:hover { background-color: #66BB6A; }
        """)
        btn_pubblica.clicked.connect(self.pubblica_messaggio)

        nuovo_msg_layout.addWidget(self.input_messaggio)
        nuovo_msg_layout.addWidget(btn_pubblica)
        layout.addLayout(nuovo_msg_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.messaggi_container = QWidget()
        self.messaggi_layout = QVBoxLayout(self.messaggi_container)
        self.messaggi_layout.setAlignment(Qt.AlignTop)  # type: ignore
        scroll.setWidget(self.messaggi_container)

        layout.addWidget(scroll)
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
                lbl_vuoto.setAlignment(Qt.AlignCenter)  # type: ignore
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
                background-color: #FFF8E1;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 8, 12, 8)

        header_layout = QHBoxLayout()
        lbl_autore = QLabel(f"Autore ID: {msg.get('id_autore', '?')}")
        lbl_autore.setStyleSheet("font-weight: bold; color: #8C1515; border: none;")
        lbl_data = QLabel(msg.get("timestamp", ""))
        lbl_data.setStyleSheet("color: gray; font-size: 11px; border: none;")
        header_layout.addWidget(lbl_autore)
        header_layout.addStretch()
        header_layout.addWidget(lbl_data)

        lbl_testo = QLabel(msg.get("testo", ""))
        lbl_testo.setWordWrap(True)
        lbl_testo.setStyleSheet("border: none; padding: 4px 0;")

        is_proprio = str(msg.get("id_autore")) == str(self.user_data.get("id"))
        is_gestore = self.user_data.get("ruolo") == "Gestore"

        card_layout.addLayout(header_layout)
        card_layout.addWidget(lbl_testo)

        if is_proprio or is_gestore:
            btn_elimina = QPushButton("Elimina")
            btn_elimina.setFixedWidth(80)
            btn_elimina.setStyleSheet("""
                QPushButton {
                    background-color: #F44336; color: white;
                    border-radius: 8px; padding: 4px; font-size: 11px;
                }
                QPushButton:hover { background-color: #EF5350; }
            """)
            msg_id = msg.get("id")
            btn_elimina.clicked.connect(lambda checked, mid=msg_id: self.elimina_messaggio(mid))
            card_layout.addWidget(btn_elimina, alignment=Qt.AlignRight)  # type: ignore

        return card

    def pubblica_messaggio(self):
        testo = self.input_messaggio.toPlainText().strip()
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
            QMessageBox.Yes | QMessageBox.No # type: ignore
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
