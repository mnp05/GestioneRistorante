from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget
from PyQt5.QtCore import Qt
from client.views.dashboard_widget import DashboardWidget
from client.views.menu_widget import MenuWidget

class MainWindow(QMainWindow):
    def __init__(self, user_data, logout_callback):
        super().__init__()
        self.user_data = user_data
        self.logout_callback = logout_callback
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Gestione Ristorante - Area Cliente")
        self.resize(800, 600)
        self.setStyleSheet("background-color: white;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header Navigation Bar (Bordeaux)
        header = QWidget()
        header.setStyleSheet("background-color: #8C1515; color: white;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)

        nome = self.user_data.get("nome", "Sconosciuto")
        cognome = self.user_data.get("cognome", "")
        lbl_user = QLabel(f"Cliente: {nome} {cognome}")
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

        # Tabs (Dashboard, Menù, Prenota)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 0; }
            QTabBar::tab {
                background-color: #C04A4A;
                color: white;
                padding: 10px 40px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #E8A38B; /* Colore più chiaro per tab attivo */
            }
        """)

        # Tab 1: Dashboard
        self.dashboard_tab = DashboardWidget(self.user_data)
        self.tabs.addTab(self.dashboard_tab, "Dashboard")

        # Tab 2: Menù
        self.menu_tab = MenuWidget()
        self.tabs.addTab(self.menu_tab, "Menù")

        # Tab 3: Prenota (Placeholder per futuri sprint)
        self.prenota_tab = QWidget()
        self.tabs.addTab(self.prenota_tab, "Prenota")

        main_layout.addWidget(self.tabs)
