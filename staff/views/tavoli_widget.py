from typing import Optional
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QMessageBox, QDialog, QFormLayout, 
                             QLineEdit, QSpinBox, QComboBox)
from PyQt5.QtCore import Qt
from staff.api_client import StaffAPIClient

COLORI_STATO = {
    "DISPONIBILE": "#4CAF50",
    "OCCUPATO": "#F44336",
    "PRENOTATO": "#FF9800",
    "IN_PULIZIA": "#9E9E9E",
}

class TavoloDialog(QDialog):
    def __init__(self, parent=None, tavolo_data=None):
        super().__init__(parent)
        self.tavolo_data = tavolo_data or {}
        self.setWindowTitle("Modifica Tavolo" if tavolo_data else "Nuovo Tavolo")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        
        self.inp_numero = QLineEdit(str(self.tavolo_data.get("numero", "")))
        if self.tavolo_data:
            self.inp_numero.setReadOnly(True) # Non permettere modifica numero se esiste
        
        self.inp_capienza = QSpinBox()
        self.inp_capienza.setRange(1, 20)
        self.inp_capienza.setValue(int(self.tavolo_data.get("capienza", 2)))
        
        self.inp_x = QSpinBox()
        self.inp_x.setRange(0, 20)
        self.inp_x.setValue(int(self.tavolo_data.get("coord_x", 0)))
        
        self.inp_y = QSpinBox()
        self.inp_y.setRange(0, 20)
        self.inp_y.setValue(int(self.tavolo_data.get("coord_y", 0)))
        
        self.combo_stato = QComboBox()
        self.combo_stato.addItems(list(COLORI_STATO.keys()))
        stato_attuale = self.tavolo_data.get("stato", "DISPONIBILE")
        self.combo_stato.setCurrentText(stato_attuale)
        
        layout.addRow("Numero Tavolo:", self.inp_numero)
        layout.addRow("Capienza Persone:", self.inp_capienza)
        layout.addRow("Posizione X (Griglia):", self.inp_x)
        layout.addRow("Posizione Y (Griglia):", self.inp_y)
        layout.addRow("Stato:", self.combo_stato)
        
        btn_layout = QHBoxLayout()
        btn_salva = QPushButton("Salva")
        btn_salva.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        btn_salva.clicked.connect(self.accept)
        
        btn_annulla = QPushButton("Annulla")
        btn_annulla.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_salva)
        btn_layout.addWidget(btn_annulla)
        
        if self.tavolo_data:
            btn_elimina = QPushButton("Elimina Tavolo")
            btn_elimina.setStyleSheet("background-color: #F44336; color: white; font-weight: bold; padding: 8px;")
            btn_elimina.clicked.connect(self.elimina)
            btn_layout.insertWidget(0, btn_elimina)
            self.vuole_eliminare = False

        layout.addRow(btn_layout)
        self.setLayout(layout)

    def elimina(self):
        risposta = QMessageBox.question(self, "Conferma", "Sei sicuro di voler eliminare questo tavolo?",
                                        QMessageBox.Yes | QMessageBox.No) # type: ignore
        if risposta == QMessageBox.Yes:
            self.vuole_eliminare = True
            self.accept()

    def get_data(self):
        return {
            "numero": self.inp_numero.text().strip(),
            "capienza": self.inp_capienza.value(),
            "coord_x": self.inp_x.value(),
            "coord_y": self.inp_y.value(),
            "stato": self.combo_stato.currentText()
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

        titolo = QLabel("Layout Sala — Clicca su un tavolo per modificarlo o cambiarne lo stato")
        titolo.setStyleSheet("font-size: 14px; font-weight: bold; color: #555;")
        layout.addWidget(titolo)

        toolbar_layout = QHBoxLayout()
        
        btn_nuovo = QPushButton("+ Nuovo Tavolo")
        btn_nuovo.setStyleSheet("background-color: #2196F3; color: white; border-radius: 5px; padding: 6px 12px; font-weight: bold;")
        btn_nuovo.clicked.connect(self.aggiungi_tavolo)
        toolbar_layout.addWidget(btn_nuovo)
        
        toolbar_layout.addStretch()

        from PyQt5.QtWidgets import QDateEdit, QCheckBox
        from PyQt5.QtCore import QDate
        
        self.chk_base = QCheckBox("Modifica Planimetria Base")
        self.chk_base.setStyleSheet("font-weight: bold; color: #8C1515;")
        self.chk_base.toggled.connect(self.load_data)
        toolbar_layout.addWidget(self.chk_base)
        
        toolbar_layout.addWidget(QLabel("Data:"))
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.dateChanged.connect(self.load_data)
        toolbar_layout.addWidget(self.date_picker)

        toolbar_layout.addStretch()

        legenda_layout = QHBoxLayout()
        for stato, colore in COLORI_STATO.items():
            lbl = QLabel(f"  {stato}  ")
            lbl.setStyleSheet(f"background-color: {colore}; color: white; padding: 4px 8px; font-size: 11px;")
            legenda_layout.addWidget(lbl)
            
        toolbar_layout.addLayout(legenda_layout)

        btn_refresh = QPushButton("Aggiorna")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #8C1515; color: white;
                border-radius: 5px; padding: 6px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #A31F1F; }
        """)
        btn_refresh.clicked.connect(self.load_data)
        toolbar_layout.addWidget(btn_refresh)

        layout.addLayout(toolbar_layout)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(12)
        layout.addLayout(self.grid_layout)

        layout.addStretch()
        self.setLayout(layout)

    def check_sovrapposizione(self, x: int, y: int, numero_escluso: Optional[str] = None) -> bool:
        for t in self.tavoli_data:
            if str(t.get("numero")) != str(numero_escluso):
                tx = int(t.get("coord_x", 0))
                ty = int(t.get("coord_y", 0))
                if tx == x and ty == y:
                    return True
        return False

    def load_data(self):
        self.date_picker.setEnabled(not self.chk_base.isChecked())
        for btn in self.bottoni_tavoli.values():
            btn.setParent(None)
        self.bottoni_tavoli.clear()

        try:
            if self.chk_base.isChecked():
                data_str = "DEFAULT"
            else:
                data_str = self.date_picker.date().toString("yyyy-MM-dd")
            self.tavoli_data = StaffAPIClient.get_tavoli(data_str)
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile caricare i tavoli:\n{e}")
            return

        max_x = max([int(t.get("coord_x", 0)) for t in self.tavoli_data] + [3])
        max_y = max([int(t.get("coord_y", 0)) for t in self.tavoli_data] + [3])

        mappa_tavoli = {}
        for t in self.tavoli_data:
            tx = int(t.get("coord_x", 0))
            ty = int(t.get("coord_y", 0))
            mappa_tavoli[(tx, ty)] = t

        for y in range(max_y + 1):
            for x in range(max_x + 1):
                tavolo = mappa_tavoli.get((x, y))
                if tavolo:
                    numero = tavolo.get("numero", "?")
                    capienza = tavolo.get("capienza", "?")
                    stato = tavolo.get("stato", "DISPONIBILE")
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
                    btn.clicked.connect(lambda checked, t=tavolo: self.modifica_tavolo(t))
                    self.grid_layout.addWidget(btn, y, x)
                    self.bottoni_tavoli[f"t_{numero}"] = btn
                else:
                    lbl = QLabel()
                    lbl.setFixedSize(130, 90)
                    lbl.setStyleSheet("""
                        QLabel {
                            border: 2px dashed #cccccc; 
                            border-radius: 10px; 
                            background-color: #fafafa;
                        }
                    """)
                    self.grid_layout.addWidget(lbl, y, x)
                    self.bottoni_tavoli[f"empty_{x}_{y}"] = lbl

    def aggiungi_tavolo(self):
        dialog = TavoloDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            dati = dialog.get_data()
            if self.chk_base.isChecked():
                dati["data"] = "DEFAULT"
            else:
                dati["data"] = self.date_picker.date().toString("yyyy-MM-dd")
                
            if not dati["numero"]:
                QMessageBox.warning(self, "Errore", "Il numero del tavolo è obbligatorio.")
                return
            if self.check_sovrapposizione(dati["coord_x"], dati["coord_y"]):
                QMessageBox.warning(self, "Errore", "La posizione (X, Y) è già occupata da un altro tavolo.")
                return
            try:
                StaffAPIClient.salva_tavolo(dati)
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e))

    def modifica_tavolo(self, tavolo_data):
        dialog = TavoloDialog(self, tavolo_data)
        if dialog.exec_() == QDialog.Accepted:
            if self.chk_base.isChecked():
                target_date = "DEFAULT"
            else:
                target_date = self.date_picker.date().toString("yyyy-MM-dd")
                
            if getattr(dialog, 'vuole_eliminare', False):
                try:
                    StaffAPIClient.elimina_tavolo(tavolo_data["numero"], data=target_date)
                    self.load_data()
                except Exception as e:
                    QMessageBox.warning(self, "Errore", str(e))
            else:
                dati = dialog.get_data()
                dati["data"] = target_date
                if self.check_sovrapposizione(dati["coord_x"], dati["coord_y"], dati["numero"]):
                    QMessageBox.warning(self, "Errore", "La posizione (X, Y) è già occupata da un altro tavolo.")
                    return
                try:
                    StaffAPIClient.salva_tavolo(dati)
                    self.load_data()
                except Exception as e:
                    QMessageBox.warning(self, "Errore", str(e))
