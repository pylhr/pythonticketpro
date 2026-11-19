"""
users.py — User management panel (admin only)
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QFormLayout, QLineEdit,
    QComboBox, QDialogButtonBox, QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from db import database as db
from ui.styles import PALETTE

ROLE_COLORS = {
    "admin": "#EF4444",
    "agent": "#F59E0B",
    "user":  "#6366F1",
}


class UsersView(QWidget):
    def __init__(self, current_user: dict):
        super().__init__()
        self.current_user = current_user
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("User Management")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        btn_new = QPushButton("+ Add User")
        btn_new.setFixedHeight(38)
        btn_new.clicked.connect(self._add_user)
        header.addWidget(btn_new)
        layout.addLayout(header)

        note = QLabel("Manage user accounts and role assignments. Admin access only.")
        note.setStyleSheet(f"color: {PALETTE['MUTED']}; font-size: 12px;")
        layout.addWidget(note)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Email", "Role", "Created"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(3, 90)
        self.table.setColumnWidth(4, 140)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            f"QTableWidget {{ alternate-background-color: {PALETTE['BG_WIDGET']}; }}"
        )
        layout.addWidget(self.table)

        actions = QHBoxLayout()
        actions.addStretch()

        btn_role = QPushButton("Change Role")
        btn_role.setObjectName("btn_secondary")
        btn_role.setFixedHeight(36)
        btn_role.clicked.connect(self._change_role)
        actions.addWidget(btn_role)

        btn_del = QPushButton("Delete User")
        btn_del.setObjectName("btn_danger")
        btn_del.setFixedHeight(36)
        btn_del.clicked.connect(self._delete_user)
        actions.addWidget(btn_del)

        layout.addLayout(actions)

    def refresh(self):
        self._users = db.get_all_users()
        self.table.setRowCount(len(self._users))
        for row, u in enumerate(self._users):
            self.table.setItem(row, 0, QTableWidgetItem(str(u["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(u["username"]))
            self.table.setItem(row, 2, QTableWidgetItem(u.get("email") or ""))
            role_item = QTableWidgetItem(u["role"].upper())
            role_item.setForeground(QColor(ROLE_COLORS.get(u["role"], PALETTE["TEXT"])))
            self.table.setItem(row, 3, role_item)
            self.table.setItem(row, 4, QTableWidgetItem((u.get("created_at") or "")[:16]))

    def _selected_user(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._users):
            return None
        return self._users[row]

    def _add_user(self):
        dlg = AddUserDialog(parent=self)
        if dlg.exec_():
            self.refresh()

    def _change_role(self):
        user = self._selected_user()
        if not user:
            return
        if user["id"] == self.current_user["id"]:
            QMessageBox.warning(self, "Error", "You cannot change your own role.")
            return
        dlg = ChangeRoleDialog(user, parent=self)
        if dlg.exec_():
            self.refresh()

    def _delete_user(self):
        user = self._selected_user()
        if not user:
            return
        if user["id"] == self.current_user["id"]:
            QMessageBox.warning(self, "Error", "You cannot delete your own account.")
            return
        reply = QMessageBox.question(
            self, "Delete User",
            f"Delete user '{user['username']}'? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            db.delete_user(user["id"])
            self.refresh()


class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add User")
        self.setFixedWidth(400)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.username_input = QLineEdit()
        self.username_input.setFixedHeight(38)
        form.addRow("Username *", self.username_input)

        self.email_input = QLineEdit()
        self.email_input.setFixedHeight(38)
        form.addRow("Email", self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(38)
        form.addRow("Password *", self.password_input)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "agent", "admin"])
        self.role_combo.setFixedHeight(38)
        form.addRow("Role", self.role_combo)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Create User")
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, "Validation", "Username and password are required.")
            return
        try:
            db.create_user(username, password, self.role_combo.currentText(), self.email_input.text().strip())
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not create user:\n{e}")


class ChangeRoleDialog(QDialog):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle(f"Change Role — {user['username']}")
        self.setFixedWidth(340)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        layout.addWidget(QLabel(f"Current role: <b>{user['role']}</b>"))

        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "agent", "admin"])
        self.role_combo.setCurrentText(user["role"])
        self.role_combo.setFixedHeight(38)
        layout.addWidget(self.role_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save(self):
        db.update_user_role(self.user["id"], self.role_combo.currentText())
        self.accept()
