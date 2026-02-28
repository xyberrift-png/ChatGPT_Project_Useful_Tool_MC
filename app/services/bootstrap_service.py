from __future__ import annotations

import logging
from pathlib import Path

from app.services.path_service import PathService
from app.services.profile_service import ProfileService

LOGGER = logging.getLogger(__name__)


class BootstrapService:
    """Performs first-run initialization for folders and default data."""

    def __init__(self, profile_service: ProfileService) -> None:
        self.profile_service = profile_service

    @staticmethod
    def ensure_directories() -> None:
        for path in (
            PathService.get_app_root(),
            PathService.data_dir(),
            PathService.logs_dir(),
            PathService.default_app_profiles_dir(),
            PathService.default_minecraft_dir(),
        ):
            path.mkdir(parents=True, exist_ok=True)

    def initialize_database_and_default_user(self) -> None:
        admin_db = self.profile_service.base_dir / "admin" / "records.db"
        if admin_db.exists():
            LOGGER.info("Database already initialized: %s", admin_db)
            return

        LOGGER.info("First run detected; initializing database and default admin user")
        if "admin" in self.profile_service.list_profiles():
            self.profile_service.ensure_profile_database("admin")
            return

        self.profile_service.create_profile("admin", "admin")
        LOGGER.info("Default admin user created")
