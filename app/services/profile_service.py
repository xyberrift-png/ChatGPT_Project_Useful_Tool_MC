from __future__ import annotations

import json
import logging
import os
import shutil
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from app.data.db import DatabaseManager
from app.services.security import SecurityService

LOGGER = logging.getLogger(__name__)
ProgressCallback = Callable[[int, int, str], None]


@dataclass(slots=True)
class Profile:
    username: str
    profile_dir: Path


class ProfileService:
    """Service for local profile authentication and import/export."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def list_profiles(self) -> list[str]:
        profiles: list[str] = []
        with os.scandir(self.base_dir) as entries:
            for entry in entries:
                if not entry.is_dir(follow_symlinks=False):
                    continue
                if Path(entry.path, "credentials.json").exists():
                    profiles.append(entry.name)
        return sorted(profiles)

    def create_profile(self, username: str, password: str) -> None:
        profile_dir = self.base_dir / username
        if profile_dir.exists():
            raise ValueError("Profile already exists")
        profile_dir.mkdir(parents=True)
        credentials = {"username": username, "password_hash": SecurityService.hash_password(password)}
        (profile_dir / "credentials.json").write_text(json.dumps(credentials, indent=2), encoding="utf-8")
        self._ensure_db(profile_dir)
        LOGGER.info("Created profile: %s", username)

    def authenticate(self, username: str, password: str) -> Profile:
        profile_dir = self.base_dir / username
        credentials_path = profile_dir / "credentials.json"
        if not credentials_path.exists():
            raise ValueError("Profile not found")
        data = json.loads(credentials_path.read_text(encoding="utf-8"))
        if not SecurityService.verify_password(password, str(data.get("password_hash", ""))):
            LOGGER.warning("Failed login attempt: %s", username)
            raise ValueError("Invalid username/password")
        self._ensure_db(profile_dir)
        LOGGER.info("User logged in: %s", username)
        return Profile(username=username, profile_dir=profile_dir)

    def ensure_profile_database(self, username: str) -> None:
        self._ensure_db(self.base_dir / username)

    def export_profile(
        self,
        username: str,
        password: str,
        export_parent: Path,
        progress: ProgressCallback | None = None,
    ) -> Path:
        profile = self.authenticate(username, password)
        export_dir = export_parent / f"{profile.username}'s profile"
        if export_dir.exists():
            shutil.rmtree(export_dir)
        self._copy_dir_with_progress(profile.profile_dir, export_dir, progress)
        return export_dir

    def import_profile(self, source_dir: Path, progress: ProgressCallback | None = None) -> str:
        credentials_path = source_dir / "credentials.json"
        db_path = source_dir / "records.db"
        if not source_dir.is_dir() or not credentials_path.exists() or not db_path.exists():
            raise ValueError("Invalid profile folder structure")

        data = json.loads(credentials_path.read_text(encoding="utf-8"))
        username = str(data.get("username", "")).strip()
        pwd_hash = str(data.get("password_hash", "")).strip()
        if not username or not pwd_hash:
            raise ValueError("Credentials data is invalid")
        if not pwd_hash.startswith(("$2a$", "$2b$", "$2y$")):
            raise ValueError("Password hash is invalid")

        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute("SELECT 1 FROM records LIMIT 1")
        except sqlite3.Error as exc:
            raise ValueError("Record database is invalid") from exc

        destination = self.base_dir / username
        if destination.exists():
            raise ValueError("Profile already exists locally")
        self._copy_dir_with_progress(source_dir, destination, progress)
        LOGGER.info("Imported profile: %s", username)
        return username

    @staticmethod
    def _copy_dir_with_progress(source: Path, destination: Path, progress: ProgressCallback | None = None) -> None:
        total_files = sum(1 for p in source.rglob("*") if p.is_file())
        total = max(1, total_files)
        destination.mkdir(parents=True, exist_ok=True)

        index = 0
        for src in source.rglob("*"):
            if not src.is_file():
                continue
            index += 1
            rel = src.relative_to(source)
            dst = destination / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            if progress:
                progress(index, total, f"Copied {rel}")

    @staticmethod
    def _ensure_db(profile_dir: Path) -> None:
        db_path = profile_dir / "records.db"
        DatabaseManager(db_path).initialize()
        LOGGER.info("Database initialized: %s", db_path)
