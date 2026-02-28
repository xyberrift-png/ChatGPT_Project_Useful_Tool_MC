from __future__ import annotations

import sqlite3
from pathlib import Path


class DatabaseManager:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize_records(self) -> None:
        with self.connect() as conn:
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

    def initialize_users(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def initialize(self) -> None:
        self.initialize_records()
        self.initialize_users()
