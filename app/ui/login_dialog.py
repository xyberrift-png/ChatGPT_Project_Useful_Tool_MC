from __future__ import annotations


    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,



class LoginDialog(QDialog):
    def __init__(self, profile_service: ProfileService, parent=None) -> None:
        super().__init__(parent)
        self.profile_service = profile_service
        self.selected_username: str | None = None

            return
        try:
            self.profile_service.authenticate(username, password)
            self.selected_username = username
            self.accept()
        except ValueError as exc:
            QMessageBox.warning(self, "Login Failed", str(exc))

