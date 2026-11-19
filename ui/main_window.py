"""
main_window.py — App shell with sidebar navigation
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget,
    QSizePolicy, QSpacerItem,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

from ui.styles import PALETTE
from ui.dashboard import DashboardView
from ui.tickets import TicketListView
from ui.users import UsersView


class MainWindow(QMainWindow):
    def __init__(self, current_user: dict):
        super().__init__()
        self.current_user = current_user
        self.setWindowTitle("TicketPro")
        self.setMinimumSize(1100, 680)
        self._build_ui()
        self._switch_page(0)

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"background-color: {PALETTE['BG_PANEL']}; border-right: 1px solid {PALETTE['BORDER']};")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(12, 20, 12, 20)
        sb_layout.setSpacing(4)

        # App name
        app_name = QLabel("🎫 TicketPro")
        app_name.setFont(QFont("Segoe UI", 15, QFont.Bold))
        app_name.setStyleSheet(f"color: {PALETTE['TEXT']}; padding: 4px 8px 16px 8px;")
        sb_layout.addWidget(app_name)

        # Nav section label
        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet(f"color: {PALETTE['MUTED']}; font-size: 10px; font-weight: 700;"
                               f"letter-spacing: 1.5px; padding: 4px 8px 4px 8px;")
        sb_layout.addWidget(nav_label)

        self.nav_buttons = []
        pages = [
            ("⊞  Dashboard",    0),
            ("🎫  Tickets",      1),
        ]
        if self.current_user["role"] == "admin":
            pages.append(("👤  Users",   2))

        for label, page_idx in pages:
            btn = QPushButton(label)
            btn.setObjectName("nav_btn")
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda _, idx=page_idx: self._switch_page(idx))
            sb_layout.addWidget(btn)
            self.nav_buttons.append((btn, page_idx))

        sb_layout.addStretch()

        # ── User badge ──
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {PALETTE['BORDER']};")
        sb_layout.addWidget(sep)

        user_frame = QFrame()
        user_frame.setStyleSheet("background: transparent;")
        uf_layout = QVBoxLayout(user_frame)
        uf_layout.setContentsMargins(8, 8, 8, 4)
        uf_layout.setSpacing(2)

        uname = QLabel(f"👤  {self.current_user['username']}")
        uname.setStyleSheet(f"color: {PALETTE['TEXT']}; font-weight: 600; font-size: 13px;")
        uf_layout.addWidget(uname)

        role_colors = {"admin": PALETTE["DANGER"], "agent": PALETTE["WARNING"], "user": PALETTE["ACCENT"]}
        role_color  = role_colors.get(self.current_user["role"], PALETTE["MUTED"])
        urole = QLabel(self.current_user["role"].upper())
        urole.setStyleSheet(f"color: {role_color}; font-size: 10px; font-weight: 700; letter-spacing: 1px;")
        uf_layout.addWidget(urole)

        btn_logout = QPushButton("Sign Out")
        btn_logout.setObjectName("btn_secondary")
        btn_logout.setFixedHeight(32)
        btn_logout.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {PALETTE['MUTED']};"
            f"border: none; text-align: left; padding: 0; font-size: 12px; }}"
            f"QPushButton:hover {{ color: {PALETTE['DANGER']}; }}"
        )
        btn_logout.clicked.connect(self._logout)
        uf_layout.addWidget(btn_logout)

        sb_layout.addWidget(user_frame)
        layout.addWidget(sidebar)

        # ── Page stack ───────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {PALETTE['BG_DARK']};")

        self.dashboard_view = DashboardView(self.current_user)
        self.tickets_view   = TicketListView(self.current_user)
        self.stack.addWidget(self.dashboard_view)   # index 0
        self.stack.addWidget(self.tickets_view)     # index 1

        if self.current_user["role"] == "admin":
            self.users_view = UsersView(self.current_user)
            self.stack.addWidget(self.users_view)   # index 2

        layout.addWidget(self.stack, 1)

    def _switch_page(self, page_idx: int):
        self.stack.setCurrentIndex(page_idx)
        # Refresh the page being switched to
        if page_idx == 0:
            self.dashboard_view.refresh()
        elif page_idx == 1:
            self.tickets_view.refresh()
        elif page_idx == 2 and hasattr(self, "users_view"):
            self.users_view.refresh()
        # Update nav button checked states
        for btn, idx in self.nav_buttons:
            btn.setChecked(idx == page_idx)

    def _logout(self):
        from PyQt5.QtWidgets import QApplication
        from ui.login import LoginWindow
        self.close()
        self._login_win = LoginWindow()
        self._login_win.login_success.connect(self._reopen)
        self._login_win.show()

    def _reopen(self, user):
        self._login_win.close()
        self._new_main = MainWindow(user)
        self._new_main.show()
