from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from app.services.profile_service import ProfileService


class LoginDialog(QDialog):
    def __init__(self, profile_service: ProfileService, parent=None) -> None:
        super().__init__(parent)
        self.profile_service = profile_service
        self.selected_username: str | None = None

        self.setWindowTitle("Welcome")
        self.setMinimumSize(520, 520)

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(0)

        center = QHBoxLayout()
        center.setAlignment(Qt.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("loginCard")
        self.card.setFixedWidth(420)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(20)

        title = QLabel("Minecraft PvP Hub")
        title.setObjectName("cardTitle")
        subtitle = QLabel("Sign in to continue")
        subtitle.setObjectName("cardSubtitle")

        self.pages = QStackedLayout()
        self.login_page = self._build_login_page()
        self.register_page = self._build_register_page()
        self.pages.addWidget(self.login_page)
        self.pages.addWidget(self.register_page)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addLayout(self.pages)

        center.addWidget(self.card)
        root.addLayout(center)

        self._apply_local_style()

    def _build_login_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Username")
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.setSpacing(12)
        form.addRow("Username", self.login_username)
        form.addRow("Password", self.login_password)

        login_btn = QPushButton("Login")
        login_btn.setObjectName("primaryButton")
        login_btn.setMinimumHeight(44)
        login_btn.clicked.connect(self.login)

        link = QLabel('<a href="#">No account? Create one</a>')
        link.setObjectName("linkLabel")
        link.setTextFormat(Qt.RichText)
        link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        link.setOpenExternalLinks(False)
        link.linkActivated.connect(lambda _: self.show_register_page())

        layout.addLayout(form)
        layout.addWidget(login_btn)
        layout.addWidget(link, alignment=Qt.AlignHCenter)
        return page

    def _build_register_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Username")
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Password")
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_confirm = QLineEdit()
        self.register_confirm.setPlaceholderText("Confirm Password")
        self.register_confirm.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.setSpacing(12)
        form.addRow("Username", self.register_username)
        form.addRow("Password", self.register_password)
        form.addRow("Confirm", self.register_confirm)

        create_btn = QPushButton("Create account")
        create_btn.setObjectName("primaryButton")
        create_btn.setMinimumHeight(44)
        create_btn.clicked.connect(self.create_profile)

        back_btn = QPushButton("Back to login")
        back_btn.setObjectName("secondaryButton")
        back_btn.setMinimumHeight(40)
        back_btn.clicked.connect(self.show_login_page)

        layout.addLayout(form)
        layout.addWidget(create_btn)
        layout.addWidget(back_btn)
        return page

    def show_register_page(self) -> None:
        self.pages.setCurrentWidget(self.register_page)

    def show_login_page(self) -> None:
        self.pages.setCurrentWidget(self.login_page)

    def create_profile(self) -> None:
        username = self.register_username.text().strip()
        password = self.register_password.text()
        confirm = self.register_confirm.text()

        if not username or not password:
            QMessageBox.warning(self, "Validation", "Username and password are required.")
            return
        if password != confirm:
            QMessageBox.warning(self, "Validation", "Passwords do not match.")
            return

        try:
            self.profile_service.create_profile(username, password)
            self.profile_service.authenticate(username, password)
            self.selected_username = username
            self.accept()
        except ValueError as exc:
            QMessageBox.warning(self, "Create Account", str(exc))

    def login(self) -> None:
        username = self.login_username.text().strip()
        password = self.login_password.text()
        if not username:
            QMessageBox.warning(self, "Login", "Please enter your username.")
            return
        try:
            self.profile_service.authenticate(username, password)
            self.selected_username = username
            self.accept()
        except ValueError as exc:
            QMessageBox.warning(self, "Login Failed", str(exc))

    def _apply_local_style(self) -> None:
        self.setStyleSheet(
            """
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #090b1a, stop:1 #1a1f3a);
            }
            #loginCard {
                background-color: rgba(18, 27, 55, 230);
                border: 1px solid rgba(90, 120, 220, 180);
                border-radius: 16px;
            }
            #cardTitle {
                color: #f2f6ff;
                font-size: 24px;
                font-weight: 700;
            }
            #cardSubtitle {
                color: #b7c8f4;
                font-size: 13px;
                margin-bottom: 6px;
            }
            QLabel { color: #dbe7ff; }
            QLineEdit {
                background-color: rgba(10, 18, 38, 230);
                color: #f0f4ff;
                border: 1px solid #4d6ed9;
                border-radius: 8px;
                padding: 8px;
                min-height: 20px;
            }
            #primaryButton {
                background-color: #3d68f0;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
                padding: 10px;
            }
            #primaryButton:hover { background-color: #5a83ff; }
            #secondaryButton {
                background-color: rgba(69, 87, 140, 180);
                color: white;
                border: 1px solid #6a83d8;
                border-radius: 10px;
                padding: 8px;
            }
            #linkLabel a {
                color: #8eb6ff;
                text-decoration: none;
                font-weight: 500;
            }
            #linkLabel a:hover { color: #a8c7ff; }
            """
        )
