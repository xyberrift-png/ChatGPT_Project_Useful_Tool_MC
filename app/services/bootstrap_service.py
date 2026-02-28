from __future__ import annotations

import logging

from app.services.path_service import PathService
from app.services.profile_service import ProfileService

LOGGER = logging.getLogger(__name__)


class BootstrapService:
    """Performs first-run initialization for folders, DB, and default users."""

    def __init__(self, profile_service: ProfileService) -> None:
        self.profile_service = profile_service

    @staticmethod
    def ensure_directories() -> None:
        for path in (
            PathService.data_dir(),
            PathService.logs_dir(),
            PathService.default_app_profiles_dir(),

        ):
            path.mkdir(parents=True, exist_ok=True)

    def initialize_database_and_default_user(self) -> None:
        count = self.profile_service.user_count()
        if count == 0:
            LOGGER.info("No users in database; creating default admin user")
            self.profile_service.create_profile("admin", "admin")
        else:
            LOGGER.info("User database already initialized with %s users", count)
