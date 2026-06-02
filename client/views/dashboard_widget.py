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

        # Card Destra (Info Buoni Regalo)
        card_buoni = QFrame()
        card_buoni.setStyleSheet("background-color: #FFFFE0; border: 1px solid #E0E0E0; border-radius: 8px;")
        buoni_layout = QVBoxLayout(card_buoni)
        
        lbl_titolo_buoni = QLabel("BUONI REGALO")
        lbl_titolo_buoni.setAlignment(Qt.AlignCenter) # type: ignore
        lbl_titolo_buoni.setStyleSheet("color: #8C1515; font-weight: bold; border: none; font-size: 16px;")

        lbl_info = QLabel("Scopri i nostri Buoni Regalo!\n\nRegala un'esperienza gastronomica unica\no riscatta un codice ricevuto in dono.")
        lbl_info.setAlignment(Qt.AlignCenter) # type: ignore
        lbl_info.setStyleSheet("border: none; color: #555; font-size: 14px;")

        lbl_cta = QLabel("Vai alla tab 'Buoni Regalo' in alto")
        lbl_cta.setAlignment(Qt.AlignCenter) # type: ignore
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
        self.setLayout(layout)
