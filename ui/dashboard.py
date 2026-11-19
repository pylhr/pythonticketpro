"""
dashboard.py — Stats overview panel
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView, QSizePolicy,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from db.database import get_stats, get_activity
from ui.styles import PALETTE, STATUS_COLORS, PRIORITY_COLORS


class StatCard(QFrame):
    def __init__(self, label: str, value: str, color: str, icon: str = ""):
        super().__init__()
        self.setObjectName("stat_card")
        self.setMinimumHeight(110)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI", 22))
        icon_lbl.setStyleSheet("background: transparent;")
        top.addWidget(icon_lbl)
        top.addStretch()
        layout.addLayout(top)

        val_lbl = QLabel(str(value))
        val_lbl.setFont(QFont("Segoe UI", 28, QFont.Bold))
        val_lbl.setStyleSheet(f"color: {color}; background: transparent;")
        layout.addWidget(val_lbl)

        lbl_lbl = QLabel(label)
        lbl_lbl.setStyleSheet(f"color: {PALETTE['MUTED']}; font-size: 12px; background: transparent;")
        layout.addWidget(lbl_lbl)


class DashboardView(QWidget):
    def __init__(self, current_user: dict):
        super().__init__()
        self.current_user = current_user
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # ── Greeting ──
        greet = QLabel(f"Welcome back, {self.current_user['username']} 👋")
        greet.setObjectName("title")
        greet.setFont(QFont("Segoe UI", 20, QFont.Bold))
        layout.addWidget(greet)

        role_lbl = QLabel(f"Role: {self.current_user['role'].upper()}")
        role_lbl.setStyleSheet(f"color: {PALETTE['MUTED']}; margin-bottom: 8px;")
        layout.addWidget(role_lbl)

        # ── Stat cards ──
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(14)
        layout.addLayout(self.stats_grid)

        # ── Recent Activity ──
        act_lbl = QLabel("RECENT ACTIVITY")
        act_lbl.setStyleSheet(f"color: {PALETTE['MUTED']}; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        layout.addWidget(act_lbl)

        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Time", "User", "Action", "Detail"])
        self.activity_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.activity_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.activity_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.activity_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.activity_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.activity_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.activity_table.verticalHeader().setVisible(False)
        self.activity_table.setAlternatingRowColors(True)
        self.activity_table.setStyleSheet(
            f"QTableWidget {{ alternate-background-color: {PALETTE['BG_WIDGET']}; }}"
        )
        self.activity_table.setMinimumHeight(260)
        layout.addWidget(self.activity_table)

        layout.addStretch()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self.refresh()

    def refresh(self):
        stats = get_stats()
        # Clear old cards
        while self.stats_grid.count():
            item = self.stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cards = [
            ("Total Tickets",  str(stats["total"]),       PALETTE["ACCENT"],  "🎫"),
            ("Open",           str(stats["open"]),         STATUS_COLORS["open"], "📬"),
            ("In Progress",    str(stats["in_progress"]), STATUS_COLORS["in_progress"], "⚙️"),
            ("Resolved",       str(stats["resolved"]),    STATUS_COLORS["resolved"], "✅"),
            ("Closed",         str(stats["closed"]),      PALETTE["MUTED"],   "🔒"),
            ("Critical",       str(stats["critical"]),    PALETTE["DANGER"],  "🔥"),
        ]
        for i, (label, value, color, icon) in enumerate(cards):
            card = StatCard(label, value, color, icon)
            self.stats_grid.addWidget(card, i // 3, i % 3)

        # Activity log
        activities = get_activity(limit=30)
        self.activity_table.setRowCount(len(activities))
        for row, act in enumerate(activities):
            ts = act["created_at"][:16] if act["created_at"] else ""
            self.activity_table.setItem(row, 0, QTableWidgetItem(ts))
            self.activity_table.setItem(row, 1, QTableWidgetItem(act.get("username") or "—"))
            action_item = QTableWidgetItem(act["action"].upper())
            action_item.setForeground(QColor(PALETTE["ACCENT2"]))
            self.activity_table.setItem(row, 2, action_item)
            ticket_ctx = f"[Ticket #{act['ticket_id']}] " if act.get("ticket_id") else ""
            detail = f"{ticket_ctx}{act.get('detail') or ''}"
            self.activity_table.setItem(row, 3, QTableWidgetItem(detail))
        self.activity_table.resizeRowsToContents()
