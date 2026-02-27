from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.data.record_repository import RecordRepository
from app.models.record import PvPRecord, RecordCategory


class RecordService:
    def __init__(self, profile_dir: Path) -> None:
        self.profile_dir = profile_dir
        self.repository = RecordRepository(profile_dir / "records.db")
        self.content_dir = profile_dir / "record_contents"
        self.content_dir.mkdir(exist_ok=True)

    def create_record(self, category: RecordCategory, rating: int, content: str, title: str = "") -> int:
        created_at = datetime.now()
        final_title = title.strip() or created_at.strftime("%Y-%m-%d")
        safe_title = "_".join(final_title.split())
        filename = f"{safe_title}_{created_at.strftime('%Y%m%d_%H%M%S')}.txt"
        (self.content_dir / filename).write_text(content, encoding="utf-8")

        record = PvPRecord(
            id=None,
            title=final_title,
            category=category,
            rating=rating,
            content=content,
            created_at=created_at,
            storage_filename=filename,
        )
        return self.repository.create(record)

    def latest(self, limit: int = 3) -> list[PvPRecord]:
        return self.repository.latest(limit)

    def list_records(self, sort_mode: str = "date") -> list[PvPRecord]:
        if sort_mode == "rating":
            return self.repository.all_by_rating()
        return self.repository.all_by_date()

    def search(self, query: str) -> list[PvPRecord]:
        if not query.strip():
            return self.repository.all_by_date()
        return self.repository.search(query)

    def get_record(self, record_id: int) -> PvPRecord | None:
        return self.repository.get(record_id)
