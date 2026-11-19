"""
tickets.py — Ticket list view + Create/Edit/View dialogs
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QDialog, QFormLayout, QDialogButtonBox,
    QMessageBox, QScrollArea, QSizePolicy, QSplitter,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont

from db import database as db
from ui.styles import PALETTE, STATUS_COLORS, PRIORITY_COLORS

STATUSES   = ["open", "in_progress", "resolved", "closed"]
PRIORITIES = ["low", "medium", "high", "critical"]
CATEGORIES = ["General", "Bug", "Feature", "Support", "Infrastructure", "Security"]


def colored_item(text: str, color: str) -> QTableWidgetItem:
    item = QTableWidgetItem(text.replace("_", " ").title())
    item.setForeground(QColor(color))
    return item


class TicketListView(QWidget):
    ticket_selected = pyqtSignal(int)

    def __init__(self, current_user: dict):
        super().__init__()
        self.current_user = current_user
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # ── Header ──
        header = QHBoxLayout()
        title = QLabel("Tickets")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        btn_new = QPushButton("+ New Ticket")
        btn_new.setFixedHeight(38)
        btn_new.clicked.connect(self._create_ticket)
        header.addWidget(btn_new)
        layout.addLayout(header)

        # ── Filters ──
        filters = QHBoxLayout()
        filters.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search tickets…")
        self.search_input.setFixedHeight(36)
        self.search_input.textChanged.connect(self.refresh)
        filters.addWidget(self.search_input, 2)

        self.filter_status = QComboBox()
        self.filter_status.addItems(["All Statuses"] + STATUSES)
        self.filter_status.setFixedHeight(36)
        self.filter_status.currentIndexChanged.connect(self.refresh)
        filters.addWidget(self.filter_status)

        self.filter_priority = QComboBox()
        self.filter_priority.addItems(["All Priorities"] + PRIORITIES)
        self.filter_priority.setFixedHeight(36)
        self.filter_priority.currentIndexChanged.connect(self.refresh)
        filters.addWidget(self.filter_priority)

        btn_clear = QPushButton("Clear")
        btn_clear.setObjectName("btn_secondary")
        btn_clear.setFixedHeight(36)
        btn_clear.clicked.connect(self._clear_filters)
        filters.addWidget(btn_clear)

        layout.addLayout(filters)

        # ── Table ──
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["#", "Title", "Status", "Priority", "Category", "Assignee", "Updated"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            f"QTableWidget {{ alternate-background-color: {PALETTE['BG_WIDGET']}; }}"
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.setColumnWidth(2, 110)
        self.table.setColumnWidth(3, 90)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 110)
        self.table.setColumnWidth(6, 140)
        self.table.doubleClicked.connect(self._open_ticket)
        layout.addWidget(self.table)

        # ── Bottom actions ──
        actions = QHBoxLayout()
        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet(f"color: {PALETTE['MUTED']};")
        actions.addWidget(self.lbl_count)
        actions.addStretch()

        btn_view = QPushButton("View / Edit")
        btn_view.setObjectName("btn_secondary")
        btn_view.setFixedHeight(36)
        btn_view.clicked.connect(self._open_ticket)
        actions.addWidget(btn_view)

        if self.current_user["role"] == "admin":
            btn_del = QPushButton("Delete")
            btn_del.setObjectName("btn_danger")
            btn_del.setFixedHeight(36)
            btn_del.clicked.connect(self._delete_ticket)
            actions.addWidget(btn_del)

        layout.addLayout(actions)

    # ── Data ──────────────────────────────────────────────────────────────
    def refresh(self):
        filters = {}
        if self.search_input.text().strip():
            filters["search"] = self.search_input.text().strip()
        status = self.filter_status.currentText()
        if status != "All Statuses":
            filters["status"] = status
        priority = self.filter_priority.currentText()
        if priority != "All Priorities":
            filters["priority"] = priority

        # Non-admin users only see their own + assigned tickets
        if self.current_user["role"] == "user":
            filters["created_by"] = self.current_user["id"]

        self._tickets = db.get_tickets(filters)
        self.table.setRowCount(len(self._tickets))

        for row, t in enumerate(self._tickets):
            self.table.setItem(row, 0, QTableWidgetItem(str(t["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(t["title"]))
            self.table.setItem(row, 2, colored_item(t["status"],   STATUS_COLORS.get(t["status"],   PALETTE["TEXT"])))
            self.table.setItem(row, 3, colored_item(t["priority"], PRIORITY_COLORS.get(t["priority"], PALETTE["TEXT"])))
            self.table.setItem(row, 4, QTableWidgetItem(t.get("category") or ""))
            self.table.setItem(row, 5, QTableWidgetItem(t.get("assignee_name") or "Unassigned"))
            self.table.setItem(row, 6, QTableWidgetItem((t["updated_at"] or "")[:16]))

        self.lbl_count.setText(f"{len(self._tickets)} ticket(s)")

    def _clear_filters(self):
        self.search_input.clear()
        self.filter_status.setCurrentIndex(0)
        self.filter_priority.setCurrentIndex(0)

    def _selected_ticket_id(self):
        rows = self.table.selectedItems()
        if not rows:
            return None
        row = self.table.currentRow()
        return self._tickets[row]["id"]

    # ── Actions ───────────────────────────────────────────────────────────
    def _create_ticket(self):
        dlg = TicketDialog(self.current_user, parent=self)
        if dlg.exec_():
            self.refresh()

    def _open_ticket(self):
        tid = self._selected_ticket_id()
        if tid is None:
            return
        dlg = TicketDetailDialog(tid, self.current_user, parent=self)
        dlg.exec_()
        self.refresh()

    def _delete_ticket(self):
        tid = self._selected_ticket_id()
        if tid is None:
            return
        reply = QMessageBox.question(
            self, "Delete Ticket",
            f"Permanently delete Ticket #{tid}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            db.delete_ticket(tid, self.current_user["id"])
            self.refresh()


# ──────────────────────────────────────────────────────────────────────────
# Create / Edit ticket dialog
# ──────────────────────────────────────────────────────────────────────────
class TicketDialog(QDialog):
    def __init__(self, current_user: dict, ticket: dict = None, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.ticket = ticket
        is_edit = ticket is not None
        self.setWindowTitle("Edit Ticket" if is_edit else "New Ticket")
        self.setMinimumWidth(520)
        self._build_ui(is_edit)
        if is_edit:
            self._populate()

    def _build_ui(self, is_edit: bool):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Short descriptive title")
        self.title_input.setFixedHeight(38)
        form.addRow("Title *", self.title_input)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Describe the issue or request…")
        self.desc_input.setFixedHeight(100)
        form.addRow("Description", self.desc_input)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(PRIORITIES)
        self.priority_combo.setCurrentText("medium")
        self.priority_combo.setFixedHeight(38)
        form.addRow("Priority", self.priority_combo)

        self.category_combo = QComboBox()
        self.category_combo.addItems(CATEGORIES)
        self.category_combo.setFixedHeight(38)
        form.addRow("Category", self.category_combo)

        # Status (edit only or admin/agent)
        if is_edit or self.current_user["role"] in ("admin", "agent"):
            self.status_combo = QComboBox()
            self.status_combo.addItems(STATUSES)
            self.status_combo.setFixedHeight(38)
            form.addRow("Status", self.status_combo)
        else:
            self.status_combo = None

        # Assignee (admin/agent only)
        if self.current_user["role"] in ("admin", "agent"):
            self.assignee_combo = QComboBox()
            self.assignee_combo.addItem("Unassigned", None)
            self._agents = db.get_agents()
            for a in self._agents:
                self.assignee_combo.addItem(a["username"], a["id"])
            self.assignee_combo.setFixedHeight(38)
            form.addRow("Assign to", self.assignee_combo)
        else:
            self.assignee_combo = None

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Save Ticket" if is_edit else "Create Ticket")
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate(self):
        t = self.ticket
        self.title_input.setText(t["title"])
        self.desc_input.setPlainText(t.get("description") or "")
        self.priority_combo.setCurrentText(t["priority"])
        if t.get("category"):
            idx = self.category_combo.findText(t["category"])
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
        if self.status_combo:
            self.status_combo.setCurrentText(t["status"])
        if self.assignee_combo and t.get("assigned_to"):
            for i in range(self.assignee_combo.count()):
                if self.assignee_combo.itemData(i) == t["assigned_to"]:
                    self.assignee_combo.setCurrentIndex(i)
                    break

    def _save(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation", "Title is required.")
            return

        assigned_to = self.assignee_combo.currentData() if self.assignee_combo else None
        status = self.status_combo.currentText() if self.status_combo else "open"

        if self.ticket:
            db.update_ticket(
                self.ticket["id"],
                self.current_user["id"],
                title=title,
                description=self.desc_input.toPlainText(),
                priority=self.priority_combo.currentText(),
                category=self.category_combo.currentText(),
                status=status,
                assigned_to=assigned_to,
            )
        else:
            db.create_ticket(
                title=title,
                description=self.desc_input.toPlainText(),
                priority=self.priority_combo.currentText(),
                category=self.category_combo.currentText(),
                created_by=self.current_user["id"],
                assigned_to=assigned_to,
            )
        self.accept()


# ──────────────────────────────────────────────────────────────────────────
# Ticket detail dialog (view + comments + activity)
# ──────────────────────────────────────────────────────────────────────────
class TicketDetailDialog(QDialog):
    def __init__(self, ticket_id: int, current_user: dict, parent=None):
        super().__init__(parent)
        self.ticket_id = ticket_id
        self.current_user = current_user
        self.setWindowTitle(f"Ticket #{ticket_id}")
        self.setMinimumSize(700, 600)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter(Qt.Vertical)

        # ── Top: ticket info ──
        top = QWidget()
        top_layout = QVBoxLayout(top)
        top_layout.setContentsMargins(24, 20, 24, 12)
        top_layout.setSpacing(10)

        title_row = QHBoxLayout()
        self.title_lbl = QLabel()
        self.title_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.title_lbl.setWordWrap(True)
        title_row.addWidget(self.title_lbl, 1)

        if self.current_user["role"] in ("admin", "agent"):
            btn_edit = QPushButton("✏  Edit")
            btn_edit.setObjectName("btn_secondary")
            btn_edit.setFixedHeight(34)
            btn_edit.clicked.connect(self._edit)
            title_row.addWidget(btn_edit)

        top_layout.addLayout(title_row)

        self.meta_lbl = QLabel()
        self.meta_lbl.setStyleSheet(f"color: {PALETTE['MUTED']}; font-size: 12px;")
        self.meta_lbl.setWordWrap(True)
        top_layout.addWidget(self.meta_lbl)

        self.desc_lbl = QLabel()
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet(f"color: {PALETTE['TEXT']}; font-size: 13px; padding: 4px 0;")
        top_layout.addWidget(self.desc_lbl)

        self.splitter.addWidget(top)

        # ── Bottom: tabs for comments & activity ──
        from PyQt5.QtWidgets import QTabWidget
        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        # Comments tab
        comments_widget = QWidget()
        comments_layout = QVBoxLayout(comments_widget)
        comments_layout.setContentsMargins(16, 12, 16, 12)
        comments_layout.setSpacing(8)

        self.comments_area = QScrollArea()
        self.comments_area.setWidgetResizable(True)
        self.comments_area.setFrameShape(QFrame.NoFrame)
        self.comments_container = QWidget()
        self.comments_vbox = QVBoxLayout(self.comments_container)
        self.comments_vbox.setSpacing(8)
        self.comments_vbox.addStretch()
        self.comments_area.setWidget(self.comments_container)
        comments_layout.addWidget(self.comments_area)

        new_comment_row = QHBoxLayout()
        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("Add a comment…")
        self.comment_input.setFixedHeight(38)
        self.comment_input.returnPressed.connect(self._post_comment)
        new_comment_row.addWidget(self.comment_input)

        btn_post = QPushButton("Post")
        btn_post.setFixedHeight(38)
        btn_post.setFixedWidth(80)
        btn_post.clicked.connect(self._post_comment)
        new_comment_row.addWidget(btn_post)

        comments_layout.addLayout(new_comment_row)
        tabs.addTab(comments_widget, "💬  Comments")

        # Activity tab
        activity_widget = QWidget()
        act_layout = QVBoxLayout(activity_widget)
        act_layout.setContentsMargins(16, 12, 16, 12)
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(3)
        self.activity_table.setHorizontalHeaderLabels(["Time", "User", "Detail"])
        self.activity_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.activity_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.activity_table.verticalHeader().setVisible(False)
        act_layout.addWidget(self.activity_table)
        tabs.addTab(activity_widget, "📋  Activity Log")

        self.splitter.addWidget(tabs)
        self.splitter.setSizes([260, 340])
        layout.addWidget(self.splitter)

    def refresh(self):
        ticket = db.get_ticket(self.ticket_id)
        if not ticket:
            return
        self._ticket = ticket
        self.setWindowTitle(f"Ticket #{ticket['id']} — {ticket['title']}")
        self.title_lbl.setText(ticket["title"])

        status_color = STATUS_COLORS.get(ticket["status"], PALETTE["TEXT"])
        prio_color   = PRIORITY_COLORS.get(ticket["priority"], PALETTE["TEXT"])

        meta = (
            f'<span style="color:{status_color}">● {ticket["status"].replace("_"," ").upper()}</span>'
            f'&nbsp;&nbsp;|&nbsp;&nbsp;'
            f'<span style="color:{prio_color}">▲ {ticket["priority"].upper()}</span>'
            f'&nbsp;&nbsp;|&nbsp;&nbsp;'
            f'Category: {ticket.get("category","")}'
            f'&nbsp;&nbsp;|&nbsp;&nbsp;'
            f'Created by: <b>{ticket.get("creator_name","")}</b>'
            f'&nbsp;&nbsp;|&nbsp;&nbsp;'
            f'Assigned: <b>{ticket.get("assignee_name") or "Unassigned"}</b>'
            f'<br>Created: {(ticket.get("created_at") or "")[:16]}'
            f'&nbsp;&nbsp;Updated: {(ticket.get("updated_at") or "")[:16]}'
        )
        self.meta_lbl.setText(meta)
        self.desc_lbl.setText(ticket.get("description") or "<em>No description provided.</em>")

        # Comments
        for i in reversed(range(self.comments_vbox.count() - 1)):
            w = self.comments_vbox.itemAt(i).widget()
            if w:
                w.deleteLater()

        comments = db.get_comments(self.ticket_id)
        for c in comments:
            frame = QFrame()
            frame.setStyleSheet(
                f"QFrame {{ background: {PALETTE['BG_WIDGET']}; border-radius: 8px; padding: 4px; }}"
            )
            fl = QVBoxLayout(frame)
            fl.setContentsMargins(12, 8, 12, 8)
            header = QLabel(f"<b>{c['username']}</b> &nbsp;<span style='color:{PALETTE['MUTED']}'>{(c['created_at'] or '')[:16]}</span>")
            header.setStyleSheet("background: transparent;")
            body = QLabel(c["body"])
            body.setWordWrap(True)
            body.setStyleSheet("background: transparent;")
            fl.addWidget(header)
            fl.addWidget(body)
            self.comments_vbox.insertWidget(self.comments_vbox.count() - 1, frame)

        # Activity
        activities = db.get_activity(ticket_id=self.ticket_id, limit=50)
        self.activity_table.setRowCount(len(activities))
        for row, act in enumerate(activities):
            self.activity_table.setItem(row, 0, QTableWidgetItem((act["created_at"] or "")[:16]))
            self.activity_table.setItem(row, 1, QTableWidgetItem(act.get("username") or "—"))
            detail = f"[{act['action'].upper()}] {act.get('detail') or ''}"
            self.activity_table.setItem(row, 2, QTableWidgetItem(detail))

    def _post_comment(self):
        text = self.comment_input.text().strip()
        if not text:
            return
        db.add_comment(self.ticket_id, self.current_user["id"], text)
        self.comment_input.clear()
        self.refresh()

    def _edit(self):
        dlg = TicketDialog(self.current_user, self._ticket, parent=self)
        if dlg.exec_():
            self.refresh()
