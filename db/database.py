"""
database.py — SQLite schema, connection, and all CRUD operations.
"""
import sqlite3
import hashlib
import os
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "ticketpro.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ──────────────────────────────────────────────
# Schema
# ──────────────────────────────────────────────
def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    UNIQUE NOT NULL,
            password    TEXT    NOT NULL,
            role        TEXT    NOT NULL DEFAULT 'user',  -- admin | agent | user
            email       TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS tickets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT,
            status      TEXT    NOT NULL DEFAULT 'open',      -- open | in_progress | resolved | closed
            priority    TEXT    NOT NULL DEFAULT 'medium',    -- low | medium | high | critical
            category    TEXT    DEFAULT 'general',
            created_by  INTEGER NOT NULL REFERENCES users(id),
            assigned_to INTEGER REFERENCES users(id),
            created_at  TEXT    DEFAULT (datetime('now')),
            updated_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS comments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id   INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            body        TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS activity_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id   INTEGER REFERENCES tickets(id) ON DELETE SET NULL,
            user_id     INTEGER REFERENCES users(id),
            action      TEXT    NOT NULL,
            detail      TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        );
        """)
        # Seed default admin if table is empty
        cur = conn.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            _seed_defaults(conn)


def _seed_defaults(conn):
    conn.execute(
        "INSERT INTO users (username, password, role, email) VALUES (?,?,?,?)",
        ("admin", _hash("admin123"), "admin", "admin@company.com"),
    )
    conn.execute(
        "INSERT INTO users (username, password, role, email) VALUES (?,?,?,?)",
        ("agent1", _hash("agent123"), "agent", "agent1@company.com"),
    )
    conn.execute(
        "INSERT INTO users (username, password, role, email) VALUES (?,?,?,?)",
        ("user1", _hash("user123"), "user", "user1@company.com"),
    )
    # Sample tickets
    conn.execute(
        """INSERT INTO tickets (title, description, status, priority, category, created_by, assigned_to)
           VALUES (?,?,?,?,?,1,2)""",
        ("Login page broken", "Users can't log in after the latest deploy.", "open", "critical", "Bug"),
    )
    conn.execute(
        """INSERT INTO tickets (title, description, status, priority, category, created_by, assigned_to)
           VALUES (?,?,?,?,?,3,2)""",
        ("Add dark mode", "Request to support a dark theme in settings.", "in_progress", "low", "Feature"),
    )
    conn.execute(
        """INSERT INTO tickets (title, description, status, priority, category, created_by)
           VALUES (?,?,?,?,?,3)""",
        ("Export to CSV missing", "The export button on reports page does nothing.", "open", "high", "Bug"),
    )


# ──────────────────────────────────────────────
# Auth helpers
# ──────────────────────────────────────────────
def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def authenticate(username: str, password: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, _hash(password)),
        ).fetchone()
    return dict(row) if row else None


# ──────────────────────────────────────────────
# Users
# ──────────────────────────────────────────────
def get_all_users():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM users ORDER BY username").fetchall()]


def get_agents():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM users WHERE role IN ('admin','agent') ORDER BY username"
        ).fetchall()]


def create_user(username, password, role, email=""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (username, password, role, email) VALUES (?,?,?,?)",
            (username, _hash(password), role, email),
        )


def delete_user(user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))


def update_user_role(user_id: int, role: str):
    with get_conn() as conn:
        conn.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))


# ──────────────────────────────────────────────
# Tickets
# ──────────────────────────────────────────────
def get_tickets(filters: dict = None):
    """Return tickets with creator/assignee names joined."""
    base = """
        SELECT t.*,
               u1.username AS creator_name,
               u2.username AS assignee_name
        FROM tickets t
        JOIN users u1 ON t.created_by = u1.id
        LEFT JOIN users u2 ON t.assigned_to = u2.id
    """
    conditions, params = [], []
    if filters:
        if filters.get("status"):
            conditions.append("t.status = ?")
            params.append(filters["status"])
        if filters.get("priority"):
            conditions.append("t.priority = ?")
            params.append(filters["priority"])
        if filters.get("assigned_to"):
            conditions.append("t.assigned_to = ?")
            params.append(filters["assigned_to"])
        if filters.get("created_by"):
            conditions.append("t.created_by = ?")
            params.append(filters["created_by"])
        if filters.get("search"):
            conditions.append("(t.title LIKE ? OR t.description LIKE ?)")
            s = f"%{filters['search']}%"
            params += [s, s]
    if conditions:
        base += " WHERE " + " AND ".join(conditions)
    base += " ORDER BY t.updated_at DESC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(base, params).fetchall()]


def get_ticket(ticket_id: int):
    with get_conn() as conn:
        row = conn.execute(
            """SELECT t.*, u1.username AS creator_name, u2.username AS assignee_name
               FROM tickets t
               JOIN users u1 ON t.created_by = u1.id
               LEFT JOIN users u2 ON t.assigned_to = u2.id
               WHERE t.id = ?""",
            (ticket_id,),
        ).fetchone()
    return dict(row) if row else None


def create_ticket(title, description, priority, category, created_by, assigned_to=None):
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO tickets (title, description, priority, category, created_by, assigned_to)
               VALUES (?,?,?,?,?,?)""",
            (title, description, priority, category, created_by, assigned_to),
        )
        tid = cur.lastrowid
        _log(conn, tid, created_by, "created", f"Ticket #{tid} created")
    return tid


def update_ticket(ticket_id, user_id, **fields):
    allowed = {"title", "description", "status", "priority", "category", "assigned_to"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    updates["updated_at"] = datetime.now().isoformat(sep=" ", timespec="seconds")
    set_clause = ", ".join(f"{k}=?" for k in updates)
    params = list(updates.values()) + [ticket_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE tickets SET {set_clause} WHERE id=?", params)
        detail = "; ".join(f"{k}→{v}" for k, v in fields.items())
        _log(conn, ticket_id, user_id, "updated", detail)


def delete_ticket(ticket_id: int, user_id: int):
    with get_conn() as conn:
        _log(conn, ticket_id, user_id, "deleted", f"Ticket #{ticket_id} deleted")
        conn.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))


# ──────────────────────────────────────────────
# Comments
# ──────────────────────────────────────────────
def get_comments(ticket_id: int):
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            """SELECT c.*, u.username FROM comments c
               JOIN users u ON c.user_id = u.id
               WHERE c.ticket_id = ?
               ORDER BY c.created_at""",
            (ticket_id,),
        ).fetchall()]


def add_comment(ticket_id: int, user_id: int, body: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO comments (ticket_id, user_id, body) VALUES (?,?,?)",
            (ticket_id, user_id, body),
        )
        conn.execute(
            "UPDATE tickets SET updated_at=datetime('now') WHERE id=?", (ticket_id,)
        )
        _log(conn, ticket_id, user_id, "commented", body[:80])


# ──────────────────────────────────────────────
# Activity log
# ──────────────────────────────────────────────
def get_activity(ticket_id: int = None, limit: int = 50):
    base = """
        SELECT a.*, u.username, t.title AS ticket_title
        FROM activity_log a
        LEFT JOIN users u ON a.user_id = u.id
        LEFT JOIN tickets t ON a.ticket_id = t.id
    """
    params = []
    if ticket_id:
        base += " WHERE a.ticket_id = ?"
        params.append(ticket_id)
    base += " ORDER BY a.created_at DESC LIMIT ?"
    params.append(limit)
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(base, params).fetchall()]


def _log(conn, ticket_id, user_id, action, detail=""):
    conn.execute(
        "INSERT INTO activity_log (ticket_id, user_id, action, detail) VALUES (?,?,?,?)",
        (ticket_id, user_id, action, detail),
    )


# ──────────────────────────────────────────────
# Dashboard stats
# ──────────────────────────────────────────────
def get_stats():
    with get_conn() as conn:
        total      = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
        open_      = conn.execute("SELECT COUNT(*) FROM tickets WHERE status='open'").fetchone()[0]
        in_prog    = conn.execute("SELECT COUNT(*) FROM tickets WHERE status='in_progress'").fetchone()[0]
        resolved   = conn.execute("SELECT COUNT(*) FROM tickets WHERE status='resolved'").fetchone()[0]
        closed     = conn.execute("SELECT COUNT(*) FROM tickets WHERE status='closed'").fetchone()[0]
        critical   = conn.execute("SELECT COUNT(*) FROM tickets WHERE priority='critical'").fetchone()[0]
        by_priority = conn.execute(
            "SELECT priority, COUNT(*) AS cnt FROM tickets GROUP BY priority"
        ).fetchall()
        by_category = conn.execute(
            "SELECT category, COUNT(*) AS cnt FROM tickets GROUP BY category ORDER BY cnt DESC LIMIT 5"
        ).fetchall()
        by_agent    = conn.execute(
            """SELECT u.username, COUNT(*) AS cnt
               FROM tickets t JOIN users u ON t.assigned_to = u.id
               GROUP BY u.username ORDER BY cnt DESC LIMIT 5"""
        ).fetchall()
    return {
        "total": total,
        "open": open_,
        "in_progress": in_prog,
        "resolved": resolved,
        "closed": closed,
        "critical": critical,
        "by_priority": [dict(r) for r in by_priority],
        "by_category": [dict(r) for r in by_category],
        "by_agent":    [dict(r) for r in by_agent],
    }
