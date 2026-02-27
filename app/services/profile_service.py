from __future__ import annotations

import json
import shutil
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from app.services.security import SecurityService


@dataclass(slots=True)
class Profile:
    username: str
    profile_dir: Path


class ProfileService:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def list_profiles(self) -> list[str]:
        return sorted([p.name for p in self.base_dir.iterdir() if p.is_dir() and (p / "credentials.json").exists()])

    def create_profile(self, username: str, password: str) -> None:
        profile_dir = self.base_dir / username
        if profile_dir.exists():
            raise ValueError("Profile already exists")
        profile_dir.mkdir(parents=True)
        credentials = {"username": username, "password_hash": SecurityService.hash_password(password)}
        (profile_dir / "credentials.json").write_text(json.dumps(credentials, indent=2), encoding="utf-8")
        self._ensure_db(profile_dir)

    def authenticate(self, username: str, password: str) -> Profile:
        profile_dir = self.base_dir / username
        credentials_path = profile_dir / "credentials.json"
        if not credentials_path.exists():
            raise ValueError("Profile not found")
        data = json.loads(credentials_path.read_text(encoding="utf-8"))
        if not SecurityService.verify_password(password, data.get("password_hash", "")):
            raise ValueError("Invalid username/password")
        self._ensure_db(profile_dir)
        return Profile(username=username, profile_dir=profile_dir)

    def export_profile(self, username: str, password: str, export_parent: Path) -> Path:
        profile = self.authenticate(username, password)
        export_dir = export_parent / f"{profile.username}'s profile"
        if export_dir.exists():
            shutil.rmtree(export_dir)
        shutil.copytree(profile.profile_dir, export_dir)
        return export_dir

    def import_profile(self, source_dir: Path) -> str:
        credentials_path = source_dir / "credentials.json"
        db_path = source_dir / "records.db"
        if not source_dir.is_dir() or not credentials_path.exists() or not db_path.exists():
            raise ValueError("Invalid profile folder structure")
        data = json.loads(credentials_path.read_text(encoding="utf-8"))
        username = data.get("username")
        pwd_hash = data.get("password_hash")
        if not username or not pwd_hash:
            raise ValueError("Credentials data is invalid")
        if not SecurityService.verify_password("test", pwd_hash) and not pwd_hash.startswith("$2"):
            raise ValueError("Password hash is invalid")
        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute("SELECT 1 FROM records LIMIT 1")
        except sqlite3.Error as exc:
            raise ValueError("Record database is invalid") from exc

        destination = self.base_dir / username
        if destination.exists():
            raise ValueError("Profile already exists locally")
        shutil.copytree(source_dir, destination)
        return username

    @staticmethod
    def _ensure_db(profile_dir: Path) -> None:
        db_path = profile_dir / "records.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    storage_filename TEXT NOT NULL
                )
                """
            )
