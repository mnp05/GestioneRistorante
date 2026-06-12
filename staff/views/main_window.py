from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget
from PyQt5.QtCore import Qt
from staff.views.tavoli_widget import TavoliWidget
from staff.views.prenotazioni_widget import PrenotazioniWidget
from staff.views.menu_widget import StaffMenuWidget
from staff.views.inventario_widget import InventarioWidget
from staff.views.dashboard_widget import StaffDashboardWidget
from staff.views.dipendenti_widget import DipendentiWidget


class StaffMainWindow(QMainWindow):
    def __init__(self, user_data, logout_callback):
        super().__init__()
        self.user_data = user_data
        self.logout_callback = logout_callback
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Gestione Ristorante - Area Staff")
        self.resize(950, 650)
        self.setStyleSheet("background-color: white;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QWidget()
        header.setStyleSheet("background-color: #8C1515; color: white;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)

        nome = self.user_data.get("nome", "")
        cognome = self.user_data.get("cognome", "")
        ruolo = self.user_data.get("ruolo", "")
        lbl_user = QLabel(f"{ruolo}: {nome} {cognome}")
        lbl_user.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(lbl_user)

        header_layout.addStretch()

        btn_logout = QPushButton("Disconnetti")
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #D45B5B;
                color: white;
                border-radius: 15px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #E57373; }
        """)
        btn_logout.clicked.connect(self.logout_callback)
        header_layout.addWidget(btn_logout)

        main_layout.addWidget(header)

        from PyQt5.QtWidgets import QStackedWidget, QSizePolicy
        # Custom Tabs using QStackedWidget + Buttons
        self.tab_bar_widget = QWidget()
        self.tab_bar_widget.setStyleSheet("background-color: #C04A4A;")
        tab_layout = QHBoxLayout(self.tab_bar_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)

        self.stacked_widget = QStackedWidget()
        
        main_layout.addWidget(self.tab_bar_widget)
        main_layout.addWidget(self.stacked_widget)
        
        self.tab_buttons = []
        
        def switch_tab(index):
            self.stacked_widget.setCurrentIndex(index)
            for i, btn in enumerate(self.tab_buttons):
                if i == index:
                    btn.setStyleSheet("background-color: #E8A38B; color: white; border: none; height: 40px; font-weight: bold; font-size: 14px;")
                else:
                    btn.setStyleSheet("background-color: transparent; color: white; border: none; height: 40px; font-weight: bold; font-size: 14px;")

        def add_custom_tab(widget, title):
            btn = QPushButton(title)
            btn.setCursor(Qt.PointingHandCursor) 
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) 
            tab_layout.addWidget(btn)
            self.stacked_widget.addWidget(widget)
            idx = self.stacked_widget.count() - 1
            btn.clicked.connect(lambda _, i=idx: switch_tab(i))
            self.tab_buttons.append(btn)

        livello = self.user_data.get("livello_accesso", "")
        ruolo = self.user_data.get("ruolo", "")

        if ruolo == "Gestore" or livello == "ACCESSO_COMPLETO":
            add_custom_tab(TavoliWidget(), "Tavoli")
            add_custom_tab(PrenotazioniWidget(), "Prenotazioni")
            add_custom_tab(StaffMenuWidget(), "Menù")
            add_custom_tab(InventarioWidget(), "Inventario")
            add_custom_tab(StaffDashboardWidget(self.user_data), "Bacheca")
            if ruolo == "Gestore":
                add_custom_tab(DipendentiWidget(self.user_data), "Dipendenti")
        else:
            if livello == "GESTIONE_PRENOTAZIONI":
                add_custom_tab(TavoliWidget(), "Tavoli")
                add_custom_tab(PrenotazioniWidget(), "Prenotazioni")
            elif livello == "GESTIONE_MENU":
                add_custom_tab(StaffMenuWidget(), "Menù")
                add_custom_tab(InventarioWidget(), "Inventario")
            
            add_custom_tab(StaffDashboardWidget(self.user_data), "Bacheca")
            
        if self.tab_buttons:
            switch_tab(0)
