"""
main.py — Entry point for TicketPro
"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from db.database import init_db
from ui.styles import APP_STYLE
from ui.login import LoginWindow
from ui.main_window import MainWindow


def main():
    # High-DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("TicketPro")
    app.setStyle("Fusion")          # base style — overridden by our stylesheet
    app.setStyleSheet(APP_STYLE)
    app.setFont(QFont("Segoe UI", 13))

    # Bootstrap database
    init_db()

    # Show login window
    login = LoginWindow()

    main_win = None

    def on_login(user: dict):
        nonlocal main_win
        login.close()
        main_win = MainWindow(user)
        main_win.show()

    login.login_success.connect(on_login)
    login.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
