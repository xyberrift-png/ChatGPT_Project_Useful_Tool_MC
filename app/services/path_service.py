from __future__ import annotations

from pathlib import Path




class PathService:
    """Path utilities for writable app data, logs, and resources."""

    @staticmethod
    def get_app_root() -> Path:
        return get_app_root()

    @classmethod
    def data_dir(cls) -> Path:
        return cls.get_app_root() / "data"

    @classmethod
    def logs_dir(cls) -> Path:
        return cls.get_app_root() / "logs"

    @classmethod
    def user_database_path(cls) -> Path:
        return cls.data_dir() / "users.db"

    @classmethod
    def default_app_profiles_dir(cls) -> Path:
        return cls.data_dir() / "profiles"

    @classmethod
    def default_minecraft_dir(cls) -> Path:
