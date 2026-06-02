from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
from PyQt5.QtCore import Qt
from client.api_client import APIClient

class DashboardWidget(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
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
        lbl_titolo_punti.setAlignment(Qt.AlignCenter)  # type: ignore
        lbl_titolo_punti.setStyleSheet("color: #8C1515; font-weight: bold; border: none;")
        
        saldo = self.user_data.get("saldo_punti", 0)
        lbl_punti = QLabel(f"{saldo} Punti")
        lbl_punti.setAlignment(Qt.AlignCenter)  # type: ignore
        lbl_punti.setStyleSheet("font-size: 24px; font-weight: bold; border: none;")
        
        lbl_prossimo = QLabel("Prossimo premio a 100")
        lbl_prossimo.setAlignment(Qt.AlignCenter)  # type: ignore
        lbl_prossimo.setStyleSheet("color: gray; border: none;")

        punti_layout.addWidget(lbl_titolo_punti)
        punti_layout.addStretch()
        punti_layout.addWidget(lbl_punti)
        punti_layout.addStretch()
        punti_layout.addWidget(lbl_prossimo)

        # Card Destra (Buoni)
        card_buoni = QFrame()
        card_buoni.setStyleSheet("background-color: #FFFFE0; border: 1px solid #E0E0E0;")
        buoni_layout = QVBoxLayout(card_buoni)
        
        lbl_titolo_buoni = QLabel("RISCATTA BUONO REGALO")
        lbl_titolo_buoni.setAlignment(Qt.AlignCenter)  # type: ignore
        lbl_titolo_buoni.setStyleSheet("color: #8C1515; font-weight: bold; border: none;")

        input_layout = QVBoxLayout()
        lbl_codice = QLabel("Codice buono:")
        lbl_codice.setStyleSheet("border: none;")
        self.input_codice = QLineEdit()
        self.input_codice.setPlaceholderText("[GIFT-XXXX-XXXX-XXXX]")
        self.input_codice.setStyleSheet("background-color: white; border: 1px dashed gray; padding: 5px;")
        input_layout.addWidget(lbl_codice)
        input_layout.addWidget(self.input_codice)

        self.btn_riscatta = QPushButton("Riscatta")
        self.btn_riscatta.setStyleSheet("""
            QPushButton {
                background-color: #E6D2B5;
                border-radius: 15px;
                padding: 10px;
                font-weight: bold;
                color: gray;
            }
            QPushButton:hover { background-color: #D4C1A3; }
        """)
        self.btn_riscatta.clicked.connect(self.handle_riscatta)

        buoni_layout.addWidget(lbl_titolo_buoni)
        buoni_layout.addLayout(input_layout)
        buoni_layout.addWidget(self.btn_riscatta, alignment=Qt.AlignCenter)

        cards_layout.addWidget(card_punti)
        cards_layout.addWidget(card_buoni)

        layout.addLayout(cards_layout)
        
        nota = QLabel("* I punti vengono accumulati automaticamente al pagamento di ciascuna prenotazione effettuata a tuo nome (1 punto per ogni euro speso).")
        nota.setStyleSheet("font-style: italic; color: gray;")
        nota.setWordWrap(True)
        layout.addSpacing(20)
        layout.addWidget(nota)

        layout.addStretch()
        self.setLayout(layout)

    def handle_riscatta(self):
        codice = self.input_codice.text()
        try:
            APIClient.riscatta_buono(codice, self.user_data.get("id"))
            QMessageBox.information(self, "Successo", "Buono riscattato con successo!")
            self.input_codice.clear()
        except Exception as e:
            QMessageBox.warning(self, "Errore", str(e))
