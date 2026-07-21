# ruff: noqa: E501
"""Application-wide visual tokens and Qt stylesheet."""

APP_STYLESHEET = """
* { font-family: 'Segoe UI', sans-serif; font-size: 13px; }
QMainWindow, QWidget { background: #10151d; color: #e7edf5; }
QFrame#navRail { background: #161d27; border-right: 1px solid #273243; }
QFrame#sidePanel { background: #151c25; border-right: 1px solid #273243; }
QFrame#inspector { background: #151c25; border-left: 1px solid #273243; }
QLabel#pageTitle { font-size: 23px; font-weight: 700; color: #f5f8fc; }
QLabel#subtitle { color: #9aabc0; }
QLabel#eyebrow { color: #60a5fa; font-size: 11px; font-weight: 700; }
QLabel#notice { background: #182638; border: 1px solid #284b70; border-radius: 8px; color: #c8ddf3; padding: 9px; }
QPushButton { background: #222d3c; border: 1px solid #34445a; border-radius: 7px; color: #e7edf5; padding: 8px 11px; }
QPushButton:hover { background: #2a3950; border-color: #4b6484; }
QPushButton:pressed { background: #172130; }
QPushButton#navButton { text-align: left; border: 0; border-radius: 6px; padding: 10px 12px; color: #aebdce; }
QPushButton#navButton:checked { background: #1c426d; color: #f4f9ff; font-weight: 700; }
QPushButton#primary { background: #2176d2; border-color: #3c94ed; color: white; font-weight: 700; }
QPushButton#primary:hover { background: #3188e4; }
QTreeView, QListWidget, QTableWidget, QPlainTextEdit { background: #111821; border: 1px solid #29374a; border-radius: 7px; alternate-background-color: #151e2a; }
QTreeView::item, QListWidget::item { padding: 7px; }
QTreeView::item:selected, QListWidget::item:selected { background: #1c426d; color: #ffffff; }
QHeaderView::section { background: #1c2633; border: 0; padding: 7px; color: #aebdce; }
QLineEdit, QComboBox, QSpinBox { background: #101821; border: 1px solid #34445a; border-radius: 6px; padding: 7px; color: #e7edf5; }
QComboBox QAbstractItemView { background: #18212d; color: #e7edf5; selection-background-color: #1c426d; }
QSlider::groove:horizontal { background: #273549; height: 5px; border-radius: 2px; }
QSlider::handle:horizontal { background: #60a5fa; width: 14px; margin: -5px 0; border-radius: 7px; }
QCheckBox { color: #b9c7d7; }
QScrollBar:vertical { background: #151d28; width: 10px; }
QScrollBar::handle:vertical { background: #3a4a60; min-height: 25px; border-radius: 5px; }
QStatusBar { background: #151c25; color: #9aabc0; border-top: 1px solid #273243; }
"""
