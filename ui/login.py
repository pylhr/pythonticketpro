"""
login.py — Login screen
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from db.database import authenticate
from ui.styles import PALETTE


class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)   # emits user dict

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TicketPro — Sign In")
        self.setFixedSize(420, 520)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ──
        header = QFrame()
        header.setFixedHeight(6)
        header.setStyleSheet(f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                             f"stop:0 {PALETTE['ACCENT']}, stop:1 {PALETTE['ACCENT2']});")
        root.addWidget(header)

        # ── Card ──
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {PALETTE['BG_PANEL']};
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(48, 52, 48, 48)
        card_layout.setSpacing(0)

        # Logo / name
        logo = QLabel("🎫  TicketPro")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFont(QFont("Segoe UI", 26, QFont.Bold))
        logo.setStyleSheet(f"color: {PALETTE['TEXT']}; background: transparent;")
        card_layout.addWidget(logo)

        tagline = QLabel("Internal Ticket Management")
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet(f"color: {PALETTE['MUTED']}; font-size: 13px; background: transparent; margin-bottom: 36px;")
        card_layout.addWidget(tagline)
        card_layout.addSpacing(32)

        # Username
        user_label = QLabel("USERNAME")
        user_label.setObjectName("section_header")
        user_label.setStyleSheet(f"color: {PALETTE['MUTED']}; font-size: 11px; font-weight: 700;"
                                 f"letter-spacing: 1px; background: transparent; margin-bottom: 6px;")
        card_layout.addWidget(user_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(44)
        card_layout.addWidget(self.username_input)
        card_layout.addSpacing(16)

        # Password
        pw_label = QLabel("PASSWORD")
        pw_label.setStyleSheet(f"color: {PALETTE['MUTED']}; font-size: 11px; font-weight: 700;"
                               f"letter-spacing: 1px; background: transparent; margin-bottom: 6px;")
        card_layout.addWidget(pw_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(44)
        self.password_input.returnPressed.connect(self._do_login)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(28)

        # Login button
        self.btn_login = QPushButton("Sign In")
        self.btn_login.setFixedHeight(46)
        self.btn_login.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.btn_login.clicked.connect(self._do_login)
        card_layout.addWidget(self.btn_login)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet(f"color: {PALETTE['DANGER']}; background: transparent; margin-top: 12px;")
        card_layout.addWidget(self.error_label)

        card_layout.addStretch()

        # Hint
        hint = QLabel("Demo: admin/admin123  ·  agent1/agent123  ·  user1/user123")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {PALETTE['MUTED']}; font-size: 11px; background: transparent;")
        card_layout.addWidget(hint)

        root.addWidget(card)

    def _do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.error_label.setText("Please enter both username and password.")
            return
        user = authenticate(username, password)
        if user:
            self.error_label.setText("")
            self.login_success.emit(user)
        else:
            self.error_label.setText("Invalid username or password.")
            self.password_input.clear()
            self.password_input.setFocus()
