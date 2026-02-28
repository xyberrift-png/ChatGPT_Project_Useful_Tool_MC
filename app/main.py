from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.services.path_service import PathService
from app.services.profile_service import ProfileService
from app.ui.login_dialog import LoginDialog
from app.ui.main_window import MainWindow
from app.ui.theme import SPACE_THEME_QSS


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(SPACE_THEME_QSS)

    profile_service = ProfileService(PathService.default_app_profiles_dir())

    login = LoginDialog(profile_service)
    if login.exec() != login.Accepted or not login.selected_username:
        return 0

    window = MainWindow(login.selected_username, profile_service)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
