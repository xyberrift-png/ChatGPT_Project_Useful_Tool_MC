from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QVBoxLayout,
)

from app.services.profile_service import ProfileService
from app.ui.widgets import AnimatedButton


class UserManagementDialog(QDialog):
    """Admin-only dialog to create/list/delete users."""

    def __init__(self, profile_service: ProfileService, current_username: str, parent=None) -> None:
        super().__init__(parent)
        self.profile_service = profile_service
        self.current_username = current_username
        self.setWindowTitle("User Management")
        self.resize(460, 420)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.users_list = QListWidget()

        create_btn = AnimatedButton("Create User")
        delete_btn = AnimatedButton("Delete Selected")
        refresh_btn = AnimatedButton("Refresh")

        create_btn.clicked.connect(self.create_user)
        delete_btn.clicked.connect(self.delete_selected_user)
        refresh_btn.clicked.connect(self.refresh_users)

        form = QFormLayout()
        form.addRow("Username", self.username_input)
        form.addRow("Password", self.password_input)

        button_row = QHBoxLayout()
        button_row.addWidget(create_btn)
        button_row.addWidget(delete_btn)
        button_row.addWidget(refresh_btn)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(button_row)
        layout.addWidget(self.users_list)
        self.setLayout(layout)

        self.refresh_users()

    def refresh_users(self) -> None:
        self.users_list.clear()
        self.users_list.addItems(self.profile_service.list_profiles())

    def create_user(self) -> None:
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or len(password) < 4:
            QMessageBox.warning(self, "Validation", "Username and 4+ char password are required.")
            return

        try:
            self.profile_service.create_profile(username, password)
        except ValueError as exc:
            QMessageBox.warning(self, "Create User", str(exc))
            return

        self.username_input.clear()
        self.password_input.clear()
        self.refresh_users()
        QMessageBox.information(self, "User Management", f"Created user: {username}")

    def delete_selected_user(self) -> None:
        item = self.users_list.currentItem()
        if item is None:
            QMessageBox.warning(self, "Delete User", "Select a user first.")
            return

        username = item.text().strip()
        try:
            self.profile_service.delete_user(username, self.current_username)
        except ValueError as exc:
            QMessageBox.warning(self, "Delete User", str(exc))
            return

        self.refresh_users()
        QMessageBox.information(self, "User Management", f"Deleted user: {username}")
