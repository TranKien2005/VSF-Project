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
QPushButton#danger { background: #7f1d1d; border-color: #b91c1c; color: #fecaca; }
QPushButton#danger:hover { background: #991b1b; }
QPushButton#preset { background: #1a2533; border: 1px solid #2e3f54; border-radius: 5px; padding: 4px 8px; font-size: 12px; color: #cbd5e1; }
QPushButton#preset:hover { background: #27384f; border-color: #475569; color: #ffffff; }

QTabBar::tab { background: #151c25; border: 1px solid #273243; border-bottom: 0; border-top-left-radius: 6px; border-top-right-radius: 6px; color: #9aabc0; padding: 8px 16px; margin-right: 4px; }
QTabBar::tab:selected { background: #1c426d; color: #ffffff; font-weight: bold; border-color: #38bdf8; }
QTabBar::tab:hover:!selected { background: #1e2836; color: #e2e8f0; }

QTreeView, QListWidget, QTableWidget, QPlainTextEdit { background: #111821; border: 1px solid #29374a; border-radius: 7px; alternate-background-color: #151e2a; }
QTreeView::item, QListWidget::item { padding: 7px; }
QTreeView::item:selected, QListWidget::item:selected { background: #1c426d; color: #ffffff; }
QHeaderView::section { background: #1c2633; border: 0; padding: 7px; color: #aebdce; }

QLineEdit, QComboBox { background: #101821; border: 1px solid #34445a; border-radius: 6px; padding: 6px 10px; color: #e7edf5; }
QComboBox QAbstractItemView { background: #18212d; color: #e7edf5; selection-background-color: #1c426d; }

QSpinBox { background: #101821; border: 1px solid #34445a; border-radius: 6px; padding: 4px 24px 4px 8px; color: #e7edf5; min-height: 28px; }
QSpinBox::up-button { subcontrol-origin: border; subcontrol-position: top right; width: 22px; border-top-right-radius: 5px; background: #1c2635; border-left: 1px solid #2a384b; border-bottom: 1px solid #2a384b; }
QSpinBox::up-button:hover { background: #2c3c54; }
QSpinBox::down-button { subcontrol-origin: border; subcontrol-position: bottom right; width: 22px; border-bottom-right-radius: 5px; background: #1c2635; border-left: 1px solid #2a384b; }
QSpinBox::down-button:hover { background: #2c3c54; }
QSpinBox::up-arrow { border-left: 4px solid transparent; border-right: 4px solid transparent; border-bottom: 5px solid #cbd5e1; width: 0; height: 0; }
QSpinBox::down-arrow { border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid #cbd5e1; width: 0; height: 0; }

QProgressBar { background: #101821; border: 1px solid #273243; border-radius: 6px; text-align: center; color: #f8fafc; font-weight: bold; min-height: 22px; }
QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4ed8, stop:1 #38bdf8); border-radius: 5px; }

QSlider::groove:horizontal { background: #273549; height: 6px; border-radius: 3px; }
QSlider::handle:horizontal { background: #38bdf8; width: 4px; margin: -8px 0; border-radius: 2px; }
QSlider::handle:horizontal:hover { background: #60a5fa; width: 6px; margin: -8px 0; }
QCheckBox { color: #b9c7d7; }
QScrollBar:vertical { background: #151d28; width: 10px; }
QScrollBar::handle:vertical { background: #3a4a60; min-height: 25px; border-radius: 5px; }
QToolTip { background: #1e293b; border: 1px solid #475569; color: #f8fafc; padding: 6px; border-radius: 4px; }
QStatusBar { background: #151c25; color: #9aabc0; border-top: 1px solid #273243; }
"""
