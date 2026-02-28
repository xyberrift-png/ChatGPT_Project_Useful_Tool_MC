from __future__ import annotations

import json
import logging
import shutil
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
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
    """Service for user auth, profile lifecycle, and import/export."""

    def __init__(self, base_dir: Path, user_db_path: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.user_db = DatabaseManager(user_db_path)
        self.user_db.initialize_users()

    def list_profiles(self) -> list[str]:
        with self.user_db.connect() as conn:
            rows = conn.execute("SELECT username FROM users ORDER BY username ASC").fetchall()
        return [str(row["username"]) for row in rows]

    def create_profile(self, username: str, password: str) -> None:
        normalized = username.strip()
        if not normalized:
            raise ValueError("Username is required")

        profile_dir = self.base_dir / normalized
        if self.user_exists(normalized) or profile_dir.exists():
            raise ValueError("Profile already exists")

        pwd_hash = SecurityService.hash_password(password)
        with self.user_db.connect() as conn:
            conn.execute(
                "INSERT INTO users(username, password_hash, created_at) VALUES(?, ?, ?)",
                (normalized, pwd_hash, datetime.now().isoformat()),
            )

        profile_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_db(profile_dir)
        LOGGER.info("User created: %s", normalized)

    def authenticate(self, username: str, password: str) -> Profile:
        normalized = username.strip()
        with self.user_db.connect() as conn:
            row = conn.execute(
                "SELECT username, password_hash FROM users WHERE username = ?",
                (normalized,),
            ).fetchone()

        if row is None:
            LOGGER.warning("Failed login attempt (unknown user): %s", normalized)
            raise ValueError("Profile not found")

        if not SecurityService.verify_password(password, str(row["password_hash"])):
            LOGGER.warning("Failed login attempt (invalid password): %s", normalized)
            raise ValueError("Invalid username/password")

        profile_dir = self.base_dir / normalized
        profile_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_db(profile_dir)
        LOGGER.info("Login success: %s", normalized)
        return Profile(username=normalized, profile_dir=profile_dir)

    def delete_user(self, username: str, current_username: str) -> None:
        target = username.strip()
        if target == current_username.strip():
            raise ValueError("You cannot delete yourself")

        if not self.user_exists(target):
            raise ValueError("User does not exist")

        with self.user_db.connect() as conn:
            conn.execute("DELETE FROM users WHERE username = ?", (target,))

        user_dir = self.base_dir / target
        if user_dir.exists():
            shutil.rmtree(user_dir)

        LOGGER.info("User deleted: %s", target)

    def user_exists(self, username: str) -> bool:
        with self.user_db.connect() as conn:
            row = conn.execute("SELECT 1 FROM users WHERE username = ?", (username.strip(),)).fetchone()
        return row is not None

    def user_count(self) -> int:
        with self.user_db.connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()
        return int(row["c"] if row else 0)

    def get_password_hash(self, username: str) -> str:
        with self.user_db.connect() as conn:
            row = conn.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
        if row is None:
            raise ValueError("User not found")
        return str(row["password_hash"])

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

        credentials = {"username": profile.username, "password_hash": self.get_password_hash(profile.username)}
        (export_dir / "credentials.json").write_text(json.dumps(credentials, indent=2), encoding="utf-8")
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
        if self.user_exists(username) or destination.exists():
            raise ValueError("Profile already exists locally")

        with self.user_db.connect() as conn:
            conn.execute(
                "INSERT INTO users(username, password_hash, created_at) VALUES(?, ?, ?)",
                (username, pwd_hash, datetime.now().isoformat()),
            )

        self._copy_dir_with_progress(source_dir, destination, progress)
        LOGGER.info("Imported profile: %s", username)
        return username

    @staticmethod
    def _copy_dir_with_progress(source: Path, destination: Path, progress: ProgressCallback | None = None) -> None:
        files = [p for p in source.rglob("*") if p.is_file() and p.name != "credentials.json"]
        total = max(1, len(files))
        destination.mkdir(parents=True, exist_ok=True)

        for index, src in enumerate(files, start=1):
            rel = src.relative_to(source)
            dst = destination / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            if progress:
                progress(index, total, f"Copied {rel}")

    @staticmethod
    def _ensure_db(profile_dir: Path) -> None:
        db_path = profile_dir / "records.db"
        DatabaseManager(db_path).initialize_records()
        LOGGER.info("Database initialized: %s", db_path)
