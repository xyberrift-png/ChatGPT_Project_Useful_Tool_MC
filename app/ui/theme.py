SPACE_THEME_QSS = """
QMainWindow, QDialog {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #050816, stop:0.5 #101b3a, stop:1 #291347);
    color: #e7efff;
}
QLabel { color: #e7efff; font-size: 14px; }
QLineEdit, QTextEdit, QComboBox, QListWidget, QSpinBox {
    background-color: rgba(12, 22, 52, 200);
    color: #ecf2ff;
    border: 1px solid #4d6ed9;
    border-radius: 8px;
    padding: 6px;
}
QPushButton {
    background-color: #2f56d2;
    color: white;
    border-radius: 10px;
    padding: 8px 12px;
    font-weight: 600;
}
QPushButton:hover { background-color: #4c74f1; }
QPushButton:pressed { background-color: #213c9d; }
QListWidget::item { padding: 6px; }
QListWidget::item:selected { background-color: #3b5ecb; }
"""
