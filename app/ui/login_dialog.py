from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from app.services.profile_service import ProfileService
from app.ui.widgets import AnimatedButton


class LoginDialog(QDialog):
    def __init__(self, profile_service: ProfileService, parent=None) -> None:
        super().__init__(parent)
        self.profile_service = profile_service
        self.selected_username: str | None = None
        self.setWindowTitle("Profile Selector")
        self.setMinimumWidth(420)

        self.profile_combo = QComboBox()
        self.profile_combo.addItems(self.profile_service.list_profiles())

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.new_username = QLineEdit()
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)

        login_btn = AnimatedButton("Login")
        create_btn = AnimatedButton("Create Profile")
        login_btn.clicked.connect(self.login)
        create_btn.clicked.connect(self.create_profile)

        form = QFormLayout()
        form.addRow("Existing Profile", self.profile_combo)
        form.addRow("Password", self.password_input)

        new_form = QFormLayout()
        new_form.addRow(QLabel("Create New Profile"))
        new_form.addRow("Username", self.new_username)
        new_form.addRow("Password", self.new_password)

        buttons = QHBoxLayout()
        buttons.addWidget(login_btn)
        buttons.addWidget(create_btn)

        root = QVBoxLayout()
        root.addLayout(form)
        root.addSpacing(8)
        root.addLayout(new_form)
        root.addLayout(buttons)
        self.setLayout(root)

    def refresh_profiles(self) -> None:
        self.profile_combo.clear()
        self.profile_combo.addItems(self.profile_service.list_profiles())

    def create_profile(self) -> None:
        username = self.new_username.text().strip()
        password = self.new_password.text()
        if not username or len(password) < 4:
            QMessageBox.warning(self, "Invalid Input", "Username and a 4+ char password are required.")
            return
        try:
            self.profile_service.create_profile(username, password)
            self.refresh_profiles()
            QMessageBox.information(self, "Success", "Profile created successfully.")
        except ValueError as exc:
            QMessageBox.warning(self, "Create Profile", str(exc))

    def login(self) -> None:
        username = self.profile_combo.currentText().strip()
        password = self.password_input.text()
        if not username:
            QMessageBox.warning(self, "Login", "Please create a profile first.")
            return
        try:
            self.profile_service.authenticate(username, password)
            self.selected_username = username
            self.accept()
        except ValueError as exc:
            QMessageBox.warning(self, "Login Failed", str(exc))
