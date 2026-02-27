from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class RecordCategory(str, Enum):
    MACE = "Mace"
    SWORD = "Sword"
    CRYSTAL = "Crystal"
    CART = "Cart"
    NETH_POT = "Neth Pot"
    DIA_POT = "Dia Pot"
    NETH_SMP = "Neth SMP"
    DIA_SMP = "Dia SMP"
    OTHER = "Other"


@dataclass(slots=True)
class PvPRecord:
    id: int | None
    title: str
    category: RecordCategory
    rating: int
    content: str
    created_at: datetime
    storage_filename: str
