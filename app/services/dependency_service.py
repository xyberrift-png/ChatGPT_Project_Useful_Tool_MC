from __future__ import annotations

import importlib.util
import sys


class DependencyService:
    """Checks runtime dependencies in development mode."""

    REQUIRED_MODULES: tuple[str, ...] = ("PySide6", "bcrypt")

    @classmethod
    def missing_runtime_modules(cls) -> list[str]:
        if getattr(sys, "frozen", False):
            return []
        missing: list[str] = []
        for module in cls.REQUIRED_MODULES:
            if importlib.util.find_spec(module) is None:
                missing.append(module)
        return missing
