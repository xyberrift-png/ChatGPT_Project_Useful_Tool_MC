from __future__ import annotations

import logging
import sys
import traceback
from types import TracebackType

from app.services.bootstrap_service import BootstrapService
from app.services.dependency_service import DependencyService
from app.services.log_service import configure_logging
from app.services.path_service import PathService
from app.services.profile_service import ProfileService

LOGGER = logging.getLogger(__name__)


def _install_global_exception_handler() -> None:
    """Install global error handling for GUI crash visibility and logging."""

    def handle_exception(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType | None,
    ) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        crash_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        LOGGER.critical("Unhandled exception:\n%s", crash_text)
        try:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(None, "Application Error", "An unexpected error occurred. Check logs for details.")
        except Exception:
            pass

    sys.excepthook = handle_exception


def _check_dev_dependencies() -> bool:
    missing = DependencyService.missing_runtime_modules()
    if not missing:
        return True

    print("Please run: pip install -r requirements.txt")
    return False


def main() -> int:
    # 1) Run bootstrap directory setup first.
    BootstrapService.ensure_directories()

    # 2) Initialize logging.
    configure_logging(PathService.logs_dir() / "app.log")
    _install_global_exception_handler()
    LOGGER.info("Application startup")

    if not _check_dev_dependencies():
        return 1

    profile_service = ProfileService(PathService.default_app_profiles_dir(), PathService.user_database_path())
    BootstrapService(profile_service).initialize_database_and_default_user()
    LOGGER.info("Database bootstrap completed")



    from app.ui.login_dialog import LoginDialog
    from app.ui.main_window import MainWindow
    from app.ui.theme import SPACE_THEME_QSS

    app = QApplication(sys.argv)
    app.setStyleSheet(SPACE_THEME_QSS)

    login = LoginDialog(profile_service)

        LOGGER.info("Application closed from login dialog")
        return 0

    window = MainWindow(login.selected_username, profile_service)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
