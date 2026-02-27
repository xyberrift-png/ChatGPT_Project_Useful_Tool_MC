from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from app.data.db import DatabaseManager
from app.models.record import PvPRecord, RecordCategory


class RecordRepository:
    def __init__(self, db_path: Path) -> None:
        self.db = DatabaseManager(db_path)
        self.db.initialize()

    def create(self, record: PvPRecord) -> int:
        with self.db.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO records(title, category, rating, content, created_at, storage_filename)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.title,
                    record.category.value,
                    record.rating,
                    record.content,
                    record.created_at.isoformat(),
                    record.storage_filename,
                ),
            )
            return int(cursor.lastrowid)

    def latest(self, limit: int = 3) -> list[PvPRecord]:
        return self._fetch(
            "SELECT * FROM records ORDER BY datetime(created_at) DESC LIMIT ?", (limit,)
        )

    def all_by_date(self) -> list[PvPRecord]:
        return self._fetch("SELECT * FROM records ORDER BY datetime(created_at) DESC")

    def all_by_rating(self) -> list[PvPRecord]:
        return self._fetch("SELECT * FROM records ORDER BY rating DESC, datetime(created_at) DESC")

    def search(self, query: str) -> list[PvPRecord]:
        pattern = f"%{query.lower()}%"
        return self._fetch(
            """
            SELECT * FROM records
            WHERE lower(title) LIKE ? OR lower(created_at) LIKE ?
            ORDER BY datetime(created_at) DESC
            """,
            (pattern, pattern),
        )

    def get(self, record_id: int) -> PvPRecord | None:
        records = self._fetch("SELECT * FROM records WHERE id = ?", (record_id,))
        return records[0] if records else None

    def _fetch(self, sql: str, params: Iterable[object] = ()) -> list[PvPRecord]:
        with self.db.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [
            PvPRecord(
                id=row["id"],
                title=row["title"],
                category=RecordCategory(row["category"]),
                rating=row["rating"],
                content=row["content"],
                created_at=datetime.fromisoformat(row["created_at"]),
                storage_filename=row["storage_filename"],
            )
            for row in rows
        ]
