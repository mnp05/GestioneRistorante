from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
from staff.api_client import StaffAPIClient

COLORI_STATO = {
    "DISPONIBILE": "#4CAF50",
    "OCCUPATO": "#F44336",
    "PRENOTATO": "#FF9800",
    "IN_PULIZIA": "#9E9E9E",
}


class TavoliWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.tavoli_data = []
        self.bottoni_tavoli = {}
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        titolo = QLabel("Layout Sala — Clicca su un tavolo per cambiare stato")
        titolo.setStyleSheet("font-size: 14px; font-weight: bold; color: #555;")
        layout.addWidget(titolo)

        legenda_layout = QHBoxLayout()
        for stato, colore in COLORI_STATO.items():
            lbl = QLabel(f"  {stato}  ")
            lbl.setStyleSheet(f"background-color: {colore}; color: white; padding: 4px 8px; font-size: 11px;")
            legenda_layout.addWidget(lbl)
        legenda_layout.addStretch()

        btn_refresh = QPushButton("Aggiorna")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #8C1515; color: white;
                border-radius: 10px; padding: 6px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #A31F1F; }
        """)
        btn_refresh.clicked.connect(self.load_data)
        legenda_layout.addWidget(btn_refresh)

        layout.addLayout(legenda_layout)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(12)
        layout.addLayout(self.grid_layout)

        layout.addStretch()
        self.setLayout(layout)

    def load_data(self):
        for btn in self.bottoni_tavoli.values():
            btn.setParent(None)
        self.bottoni_tavoli.clear()

        try:
            self.tavoli_data = StaffAPIClient.get_tavoli()
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile caricare i tavoli:\n{e}")
            return

        for tavolo in self.tavoli_data:
            numero = tavolo.get("numero", "?")
            capienza = tavolo.get("capienza", "?")
            stato = tavolo.get("stato", "DISPONIBILE")
            x = int(tavolo.get("coord_x", 0))
            y = int(tavolo.get("coord_y", 0))
            colore = COLORI_STATO.get(stato, "#607D8B")

            btn = QPushButton(f"T{numero}\n{capienza} posti\n{stato}")
            btn.setFixedSize(130, 90)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colore}; color: white;
                    border-radius: 10px; font-weight: bold; font-size: 12px;
                }}
                QPushButton:hover {{ opacity: 0.8; border: 2px solid #333; }}
            """)
            btn.clicked.connect(lambda checked, n=numero: self.cambia_stato(n))
            self.grid_layout.addWidget(btn, y, x)
            self.bottoni_tavoli[numero] = btn

    def cambia_stato(self, numero_tavolo):
        tavolo = next((t for t in self.tavoli_data if str(t.get("numero")) == str(numero_tavolo)), None)
        if not tavolo:
            return

        stati = list(COLORI_STATO.keys())
        stato_attuale = tavolo.get("stato", "DISPONIBILE")

        from PyQt5.QtWidgets import QInputDialog
        nuovo_stato, ok = QInputDialog.getItem(
            self, f"Tavolo {numero_tavolo}",
            f"Stato attuale: {stato_attuale}\nSeleziona nuovo stato:",
            stati, stati.index(stato_attuale) if stato_attuale in stati else 0, False
        )

        if ok and nuovo_stato != stato_attuale:
            try:
                success = StaffAPIClient.aggiorna_stato_tavolo(numero_tavolo, nuovo_stato)
                if success:
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile aggiornare lo stato del tavolo.")
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))
