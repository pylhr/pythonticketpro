"""
styles.py — Dark-slate theme with indigo accents.
Palette:
  BG_DARK   #0F1117   main window background
  BG_PANEL  #1A1D27   cards / panels
  BG_WIDGET #22263A   inputs / tables
  ACCENT    #6366F1   indigo primary
  ACCENT2   #818CF8   indigo light (hover)
  TEXT      #E2E8F0   primary text
  MUTED     #64748B   secondary text
  BORDER    #2D3148   subtle borders
  SUCCESS   #22C55E
  WARNING   #F59E0B
  DANGER    #EF4444
  INFO      #38BDF8
"""

PALETTE = {
    "BG_DARK":   "#0F1117",
    "BG_PANEL":  "#1A1D27",
    "BG_WIDGET": "#22263A",
    "ACCENT":    "#6366F1",
    "ACCENT2":   "#818CF8",
    "TEXT":      "#E2E8F0",
    "MUTED":     "#64748B",
    "BORDER":    "#2D3148",
    "SUCCESS":   "#22C55E",
    "WARNING":   "#F59E0B",
    "DANGER":    "#EF4444",
    "INFO":      "#38BDF8",
}

PRIORITY_COLORS = {
    "critical": "#EF4444",
    "high":     "#F59E0B",
    "medium":   "#6366F1",
    "low":      "#22C55E",
}

STATUS_COLORS = {
    "open":        "#38BDF8",
    "in_progress": "#F59E0B",
    "resolved":    "#22C55E",
    "closed":      "#64748B",
}

APP_STYLE = f"""
/* ── Global ── */
QWidget {{
    background-color: {PALETTE['BG_DARK']};
    color: {PALETTE['TEXT']};
    font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}}

/* ── Scroll bars ── */
QScrollBar:vertical {{
    background: {PALETTE['BG_PANEL']};
    width: 8px; border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {PALETTE['BORDER']};
    border-radius: 4px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {PALETTE['MUTED']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* ── QPushButton ── */
QPushButton {{
    background-color: {PALETTE['ACCENT']};
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 7px 18px;
    font-weight: 600;
}}
QPushButton:hover  {{ background-color: {PALETTE['ACCENT2']}; }}
QPushButton:pressed {{ background-color: #4F52C8; }}
QPushButton:disabled {{ background-color: {PALETTE['BORDER']}; color: {PALETTE['MUTED']}; }}

QPushButton#btn_danger {{
    background-color: {PALETTE['DANGER']};
}}
QPushButton#btn_danger:hover {{ background-color: #F87171; }}

QPushButton#btn_secondary {{
    background-color: {PALETTE['BG_WIDGET']};
    color: {PALETTE['TEXT']};
    border: 1px solid {PALETTE['BORDER']};
}}
QPushButton#btn_secondary:hover {{ background-color: {PALETTE['BORDER']}; }}

/* ── QLineEdit / QTextEdit / QComboBox ── */
QLineEdit, QTextEdit, QComboBox, QSpinBox {{
    background-color: {PALETTE['BG_WIDGET']};
    border: 1px solid {PALETTE['BORDER']};
    border-radius: 6px;
    padding: 6px 10px;
    color: {PALETTE['TEXT']};
    selection-background-color: {PALETTE['ACCENT']};
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border-color: {PALETTE['ACCENT']};
}}
QComboBox::drop-down {{
    border: none;
    width: 28px;
}}
QComboBox::down-arrow {{
    image: none;
    width: 0;
}}
QComboBox QAbstractItemView {{
    background-color: {PALETTE['BG_PANEL']};
    border: 1px solid {PALETTE['BORDER']};
    selection-background-color: {PALETTE['ACCENT']};
    outline: none;
}}

/* ── QTableWidget ── */
QTableWidget {{
    background-color: {PALETTE['BG_PANEL']};
    gridline-color: {PALETTE['BORDER']};
    border: 1px solid {PALETTE['BORDER']};
    border-radius: 8px;
    outline: none;
}}
QTableWidget::item {{
    padding: 6px 10px;
}}
QTableWidget::item:selected {{
    background-color: {PALETTE['ACCENT']};
    color: #FFFFFF;
}}
QHeaderView::section {{
    background-color: {PALETTE['BG_WIDGET']};
    color: {PALETTE['MUTED']};
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {PALETTE['BORDER']};
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ── QTabWidget ── */
QTabWidget::pane {{
    border: 1px solid {PALETTE['BORDER']};
    border-radius: 8px;
    background-color: {PALETTE['BG_PANEL']};
}}
QTabBar::tab {{
    background: {PALETTE['BG_WIDGET']};
    color: {PALETTE['MUTED']};
    padding: 8px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: {PALETTE['ACCENT']};
    color: #FFFFFF;
}}

/* ── QLabel ── */
QLabel#title {{
    font-size: 22px;
    font-weight: 700;
    color: {PALETTE['TEXT']};
}}
QLabel#subtitle {{
    font-size: 13px;
    color: {PALETTE['MUTED']};
}}
QLabel#section_header {{
    font-size: 11px;
    font-weight: 700;
    color: {PALETTE['MUTED']};
    letter-spacing: 1px;
}}

/* ── Sidebar nav buttons ── */
QPushButton#nav_btn {{
    background: transparent;
    color: {PALETTE['MUTED']};
    border: none;
    border-radius: 8px;
    text-align: left;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton#nav_btn:hover {{
    background: {PALETTE['BG_WIDGET']};
    color: {PALETTE['TEXT']};
}}
QPushButton#nav_btn:checked {{
    background: {PALETTE['ACCENT']};
    color: #FFFFFF;
    font-weight: 600;
}}

/* ── Stat cards ── */
QFrame#stat_card {{
    background-color: {PALETTE['BG_PANEL']};
    border: 1px solid {PALETTE['BORDER']};
    border-radius: 10px;
}}

/* ── Message/alert frames ── */
QFrame#alert_info {{
    background-color: #1E3A5F;
    border-left: 3px solid {PALETTE['INFO']};
    border-radius: 4px;
}}
"""
