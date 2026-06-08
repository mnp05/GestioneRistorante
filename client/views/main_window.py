from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget
from PyQt5.QtCore import Qt
from client.views.dashboard_widget import DashboardWidget
from client.views.menu_widget import MenuWidget
from client.views.prenota_widget import PrenotaWidget
from client.views.buoni_widget import BuoniWidget

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

        # Tab 1: Dashboard
        self.dashboard_tab = DashboardWidget(self.user_data, self.logout_callback)
        add_custom_tab(self.dashboard_tab, "Dashboard")

        # Tab 2: Menù
        self.menu_tab = MenuWidget(self.user_data)
        add_custom_tab(self.menu_tab, "Menù")

        # Tab 3: Prenota
        self.prenota_tab = PrenotaWidget(self.user_data)
        add_custom_tab(self.prenota_tab, "Prenota")

        # Tab 4: Buoni Regalo
        self.buoni_tab = BuoniWidget(self.user_data)
        add_custom_tab(self.buoni_tab, "Buoni Regalo")
        
        if self.tab_buttons:
            switch_tab(0)
