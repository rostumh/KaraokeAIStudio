from __future__ import annotations

DARK_STYLESHEET = """
QWidget {
    background-color: #101620;
    color: #e7edf7;
    font-family: "Segoe UI";
    font-size: 10pt;
}
QMainWindow, QDialog { background-color: #0b1018; }
QWidget#sidebar { background-color: #0c121c; border-right: 1px solid #202c3c; }
QWidget#topBar, QWidget#transportBar { background-color: #121a26; border-bottom: 1px solid #263448; }
QFrame#panel, QFrame#card { background-color: #151e2b; border: 1px solid #263448; border-radius: 10px; }
QLabel#brandTitle { color: #f8fafc; font-size: 16pt; font-weight: 700; }
QLabel#brandCaption { color: #6f819a; font-size: 8pt; }
QLabel#pageTitle { color: #f8fafc; font-size: 19pt; font-weight: 650; }
QLabel#sectionTitle { color: #f2f6fc; font-size: 12pt; font-weight: 600; }
QLabel#muted, QLabel#timeLabel { color: #8d9db2; }
QLabel#emptyTitle { color: #f8fafc; font-size: 15pt; font-weight: 600; }
QLabel#emptyText { color: #8d9db2; }
QPushButton, QToolButton {
    background-color: #1a2534;
    color: #dce6f4;
    border: 1px solid #2b3b51;
    border-radius: 7px;
    min-height: 30px;
    padding: 4px 11px;
}
QPushButton:hover, QToolButton:hover { background-color: #223147; border-color: #3b526f; }
QPushButton:pressed, QToolButton:pressed { background-color: #111a27; }
QPushButton:checked { background-color: #2359d8; border-color: #4d7cf0; color: white; }
QPushButton#primaryButton { background-color: #316fea; border-color: #4b82ef; color: white; font-weight: 600; }
QPushButton#primaryButton:hover { background-color: #3e7bf1; }
QPushButton#navButton { text-align: left; padding: 8px 13px; border: 0; background: transparent; }
QPushButton#navButton:hover { background-color: #172233; }
QPushButton#navButton:checked { background-color: #1b3154; color: #80aaff; border-left: 3px solid #5790ff; }
QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #0d141f;
    color: #e7edf7;
    border: 1px solid #2a3a50;
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: #316fea;
}
QSpinBox, QDoubleSpinBox { padding-right: 30px; }
QSpinBox::up-button, QDoubleSpinBox::up-button { width: 26px; subcontrol-position: top right; }
QSpinBox::down-button, QDoubleSpinBox::down-button { width: 26px; subcontrol-position: bottom right; }
QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus { border-color: #5790ff; }
QComboBox::drop-down { border: 0; width: 24px; }
QComboBox QAbstractItemView { background-color: #151f2d; border: 1px solid #31435a; selection-background-color: #275cc9; }
QTabWidget::pane { border: 1px solid #263448; background: #111925; border-radius: 8px; }
QTabBar::tab { background: #121b28; color: #8fa0b5; padding: 9px 15px; border: 1px solid #263448; }
QTabBar::tab:selected { background: #1b2a40; color: #f3f7fd; border-bottom: 2px solid #5790ff; }
QHeaderView::section { background-color: #182231; color: #b6c3d4; border: 0; border-bottom: 1px solid #2b3a4e; padding: 8px; }
QTableView, QListWidget, QTreeWidget {
    background-color: #101722;
    alternate-background-color: #141e2b;
    border: 1px solid #263448;
    border-radius: 7px;
    gridline-color: #263448;
    selection-background-color: #244f9d;
}
QProgressBar { background-color: #0c121b; border: 1px solid #29394f; border-radius: 5px; text-align: center; height: 12px; }
QProgressBar::chunk { background-color: #3d7af0; border-radius: 4px; }
QSlider::groove:horizontal { background: #28374b; height: 5px; border-radius: 2px; }
QSlider::handle:horizontal { background: #6c9cff; width: 14px; margin: -5px 0; border-radius: 7px; }
QScrollBar:vertical { background: #0e151f; width: 11px; }
QScrollBar::handle:vertical { background: #304158; border-radius: 5px; min-height: 28px; }
QDockWidget { color: #dce5f1; font-weight: 600; }
QDockWidget::title { background: #151e2b; padding: 8px; border-bottom: 1px solid #2a394e; }
QStatusBar { background-color: #121a26; color: #8fa0b5; border-top: 1px solid #263448; }
QMenuBar { background: #0d131d; border-bottom: 1px solid #202c3c; }
QMenuBar::item:selected, QMenu::item:selected { background: #244b8c; }
QMenu { background: #151e2b; border: 1px solid #2b3b51; padding: 5px; }
QToolBar { background: #111925; border-bottom: 1px solid #263448; spacing: 4px; padding: 4px; }
QToolTip { background-color: #202a3a; color: white; border: 1px solid #3a4a63; padding: 5px; }
QSplitter::handle { background: #263448; }
"""

LIGHT_STYLESHEET = """
QWidget { background:#f4f7fb; color:#172033; font-family:'Segoe UI'; font-size:10pt; }
QMainWindow,QDialog { background:#eef3f9; }
QWidget#sidebar,QToolBar,QMenuBar,QStatusBar { background:#ffffff; color:#172033; border-color:#c8d3e1; }
QFrame#panel,QFrame#card { background:#ffffff; border:1px solid #c8d3e1; border-radius:9px; }
QGroupBox { background:#ffffff; border:1px solid #c8d3e1; border-radius:9px; margin-top:16px; padding:16px 10px 10px 10px; font-weight:600; }
QGroupBox::title { subcontrol-origin:margin; subcontrol-position:top left; left:12px; padding:0 6px; background:#f4f7fb; color:#172033; }
QLabel#brandTitle,QLabel#pageTitle,QLabel#sectionTitle { color:#101828; font-weight:650; }
QLabel#muted,QLabel#brandCaption { color:#667085; }
QPushButton,QToolButton { background:#ffffff; color:#172033; border:1px solid #c9d3e1; border-radius:7px; min-height:30px; padding:4px 11px; }
QPushButton:hover,QToolButton:hover { background:#edf4ff; border-color:#7aa7ef; }
QPushButton#primaryButton,QPushButton:checked { background:#2767dc; color:white; border-color:#2767dc; }
QPushButton#navButton { text-align:left; border:0; background:transparent; }
QPushButton#navButton:checked { background:#e9f1ff; color:#1849a9; border-left:3px solid #2767dc; }
QLineEdit,QPlainTextEdit,QComboBox,QSpinBox,QDoubleSpinBox,QTableView,QListWidget,QTreeWidget { background:#ffffff; color:#172033; border:1px solid #cbd5e1; border-radius:6px; padding:6px; selection-background-color:#3977df; }
QHeaderView::section { background:#e9eef5; color:#344054; border:0; padding:8px; }
QTabWidget::pane { background:#ffffff; border:1px solid #d3dce8; }
QTabBar::tab { background:#edf2f7; color:#475467; padding:9px 15px; }
QTabBar::tab:selected { background:#ffffff; color:#1849a9; border-bottom:2px solid #2767dc; }
QMenu { background:#ffffff; color:#172033; border:1px solid #cbd5e1; }
QMenu::item:selected { background:#e9f1ff; }
QProgressBar { background:#e5eaf0; border:1px solid #cbd5e1; border-radius:5px; text-align:center; }
QProgressBar::chunk { background:#2767dc; }

QDockWidget::title { background:#e9eef5; color:#172033; padding:8px; }
QScrollBar:vertical { background:#eef2f6; width:12px; }
QScrollBar::handle:vertical { background:#aab8ca; min-height:28px; border-radius:5px; }
QComboBox QAbstractItemView { background:#ffffff; color:#172033; selection-background-color:#2767dc; selection-color:#ffffff; }
"""
