import sys
import os

# Aggiungi la root del progetto al path di sistema per poter importare 'client'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtWidgets import QApplication
from client.views.login_window import LoginWindow
from client.views.main_window import MainWindow

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_win = None
        self.main_win = None

    def start(self):
        self.show_login()
        sys.exit(self.app.exec_())

    def show_login(self):
        if self.main_win:
            self.main_win.close()
            self.main_win = None
        
        self.login_win = LoginWindow(self.on_login_success)
        self.login_win.show()

    def on_login_success(self, user_data):
        if self.login_win:
            self.login_win.close()
            self.login_win = None
        
        self.main_win = MainWindow(user_data, self.show_login)
        self.main_win.show()

if __name__ == "__main__":
    controller = AppController()
    controller.start()
