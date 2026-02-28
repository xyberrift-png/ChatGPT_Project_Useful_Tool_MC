from __future__ import annotations

import sys
from pathlib import Path


class PathService:
    """Path utilities that work in both source and frozen distributions."""

    @staticmethod
    def get_app_root() -> Path:
        """Return application root for Python and PyInstaller execution modes."""
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent
        return Path(__file__).resolve().parents[2]

    @classmethod
    def data_dir(cls) -> Path:
        return cls.get_app_root() / "data"

    @classmethod
    def logs_dir(cls) -> Path:
        return cls.get_app_root() / "logs"

    @classmethod
    def default_app_profiles_dir(cls) -> Path:
        return cls.data_dir() / "profiles"

    @classmethod
    def default_minecraft_dir(cls) -> Path:
        return cls.get_app_root() / ".minecraft"
