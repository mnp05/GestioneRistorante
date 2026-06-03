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

        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 0; }
            QTabBar::tab {
                background-color: #C04A4A;
                color: white;
                height: 40px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #E8A38B;
            }
        """)

        self.tabs.addTab(TavoliWidget(), "Tavoli")
        self.tabs.addTab(PrenotazioniWidget(), "Prenotazioni")
        self.tabs.addTab(StaffMenuWidget(), "Menù")
        self.tabs.addTab(InventarioWidget(), "Inventario")
        self.tabs.addTab(StaffDashboardWidget(self.user_data), "Bacheca")

        if self.user_data.get("ruolo") == "Gestore":
            self.tabs.addTab(DipendentiWidget(self.user_data), "Dipendenti")

        main_layout.addWidget(self.tabs)
