from __future__ import annotations

import os
import shutil
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Literal

from app.services.path_service import PathService

InstallMode = Literal["append", "overwrite"]
ProgressCallback = Callable[[int, int, str], None]


class ModInstallerService:
    @staticmethod
    def default_minecraft_dir() -> Path:
        return PathService.default_minecraft_dir()

    @staticmethod
    def collect_mod_files(selection: Iterable[Path], progress: ProgressCallback | None = None) -> list[Path]:
        seen: set[str] = set()
        collected: list[Path] = []

        candidates = list(selection)
        total = max(1, len(candidates))
        for index, item in enumerate(candidates, start=1):
            if item.is_file() and item.suffix.lower() == ".jar":
                key = str(item.resolve())
                if key not in seen:
                    seen.add(key)
                    collected.append(item)
            elif item.is_dir():
                for jar in ModInstallerService._iter_jar_files(item):
                    key = str(jar.resolve())
                    if key not in seen:
                        seen.add(key)
                        collected.append(jar)
            if progress:
                progress(index, total, f"Scanning {item.name}")
        return collected

    @staticmethod
    def _iter_jar_files(root: Path) -> Iterable[Path]:
        stack: list[Path] = [root]
        while stack:
            current = stack.pop()
            try:
                with os.scandir(current) as iterator:
                    for entry in iterator:
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(Path(entry.path))
                        elif entry.is_file(follow_symlinks=False) and entry.name.lower().endswith(".jar"):
                            yield Path(entry.path)
            except OSError:
                continue

    def install(
        self,
        selected_files: list[Path],
        minecraft_dir: Path,
        mode: InstallMode,
        replace_duplicates: bool,
        progress: ProgressCallback | None = None,
    ) -> list[str]:

        installed: list[str] = []

        if mode == "overwrite":
            for existing in mods_dir.glob("*.jar"):
                existing.unlink()

        total = max(1, len(selected_files))
        for index, source in enumerate(selected_files, start=1):
            target = mods_dir / source.name
            if target.exists():
                if replace_duplicates:
                    target.unlink()
                else:
                    if progress:
                        progress(index, total, f"Skipped duplicate {source.name}")
                    continue
            shutil.copy2(source, target)
            installed.append(source.name)
            if progress:
                progress(index, total, f"Installed {source.name}")

        return installed

    @staticmethod
    def files_to_delete_on_overwrite(minecraft_dir: Path) -> list[str]:
        mods_dir = minecraft_dir / "mods"
        if not mods_dir.exists():
            return []
        return sorted([p.name for p in mods_dir.glob("*.jar")])
