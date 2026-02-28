from __future__ import annotations

import os
from pathlib import Path


class PathService:
    """Utility helpers for OS-specific paths."""

    @staticmethod
    def default_app_profiles_dir() -> Path:
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "MinecraftPvPHub" / "profiles"
        return Path.cwd() / "local_data" / "profiles"

    @staticmethod
    def default_minecraft_dir() -> Path:
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / ".minecraft"
        return Path.home() / "AppData" / "Roaming" / ".minecraft"
