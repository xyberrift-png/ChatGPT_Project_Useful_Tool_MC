from __future__ import annotations

import os
import sys
from pathlib import Path


def get_app_root() -> Path:
    """Return writable application root for source and frozen execution."""
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            _ = Path(getattr(sys, "_MEIPASS"))
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def get_minecraft_directory() -> Path:
    """Return the default Windows Minecraft directory (%APPDATA%/.minecraft)."""
    return Path(os.environ["APPDATA"]) / ".minecraft"
